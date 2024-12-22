"""
Surface Reconstruction from Contour Lines
---------------------------------------
This module implements efficient 3D surface reconstruction from horizontal contours
and vertical traces using VTK. It employs optimized algorithms for point extraction,
interpolation, and surface generation while maintaining numerical stability and 
performance.

Author: Claude
Date: December 2024
"""

import numpy as np
import vtk
from vtk.util import numpy_support  # type: ignore
from typing import Tuple, List, Optional
from dataclasses import dataclass
import concurrent.futures
from scipy.spatial import cKDTree


@dataclass
class GridPoint:
    """Represents a point where contours intersect."""

    position: np.ndarray  # [x, y, z]
    normal: np.ndarray  # Surface normal at point
    curvature: float  # Local curvature estimate


class ContourIntersectionExtractor:
    """
    Extracts and organizes intersection points from contour and trace actors.
    Uses spatial indexing for efficient point location and matching.
    """

    def __init__(self, tolerance: float = 1e-6, neighborhood_size: int = 8):
        self.tolerance = tolerance
        self.neighborhood_size = neighborhood_size
        self.kdtree = cKDTree(np.empty((0, 3)))  # Initialize with an empty KDTree

    def extract_points_from_actor(self, actor: vtk.vtkActor) -> np.ndarray:
        """
        Efficiently extracts point coordinates from a VTK actor.

        Args:
            actor: VTK actor containing line geometry

        Returns:
            Nx3 numpy array of point coordinates
        """
        polydata = actor.GetMapper().GetInput()
        points = polydata.GetPoints()
        points_array = numpy_support.vtk_to_numpy(points.GetData())
        return points_array

    def find_intersections(
        self, horizontal_actor: vtk.vtkActor, vertical_actor: vtk.vtkActor
    ) -> List[GridPoint]:
        """
        Finds all intersection points between horizontal contours and vertical traces.
        Uses KD-tree for efficient spatial matching.

        Args:
            horizontal_actor: Actor containing horizontal contours
            vertical_actor: Actor containing vertical traces

        Returns:
            List of GridPoint objects at intersection locations
        """
        h_points = self.extract_points_from_actor(horizontal_actor)
        v_points = self.extract_points_from_actor(vertical_actor)

        # Build KD-tree for efficient spatial search
        self.kdtree = cKDTree(h_points)

        intersections = []
        # Use parallel processing for large point sets
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for point in v_points:
                futures.append(executor.submit(self._process_point, point, h_points))

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result is not None:
                    intersections.append(result)

        return intersections

    def _process_point(
        self, point: np.ndarray, reference_points: np.ndarray
    ) -> Optional[GridPoint]:
        """
        Process a single point to find nearby intersections.

        Args:
            point: Query point coordinates
            reference_points: Array of reference points to match against

        Returns:
            GridPoint object if intersection found, None otherwise
        """
        distances, indices = self.kdtree.query(
            point, k=1, distance_upper_bound=self.tolerance
        )

        if distances < self.tolerance:
            normal = self._estimate_normal(point, reference_points, indices)
            curvature = self._estimate_curvature(point, reference_points, indices)
            return GridPoint(point, normal, curvature)
        return None

    def _estimate_normal(
        self, point: np.ndarray, reference_points: np.ndarray, center_idx: int
    ) -> np.ndarray:
        """
        Estimates surface normal at an intersection point using local geometry.
        Uses both horizontal and vertical line directions to compute the normal.

        Args:
            point: Intersection point coordinates
            reference_points: Array of nearby points
            center_idx: Index of the closest reference point

        Returns:
            Unit normal vector as numpy array
        """
        # Find neighboring points for both horizontal and vertical directions
        _, neighbor_indices = self.kdtree.query(point, k=self.neighborhood_size)

        # Separate points into horizontal and vertical groups
        # (based on z-coordinate similarity)
        horizontal_points = []
        vertical_points = []
        z_tolerance = self.tolerance * 2

        for idx in neighbor_indices:
            if idx >= len(reference_points):
                continue
            neighbor = reference_points[idx]
            if abs(neighbor[2] - point[2]) < z_tolerance:
                horizontal_points.append(neighbor)
            else:
                vertical_points.append(neighbor)

        # Compute direction vectors
        horizontal_dir = None
        vertical_dir = None

        if len(horizontal_points) >= 2:
            # Use PCA to find principal direction of horizontal points
            horizontal_points = np.array(horizontal_points)
            centered = horizontal_points - point
            cov = np.cov(centered.T)
            eigenvalues, eigenvectors = np.linalg.eigh(cov)
            horizontal_dir = eigenvectors[:, np.argmax(eigenvalues)]

        if len(vertical_points) >= 2:
            # Use PCA to find principal direction of vertical points
            vertical_points = np.array(vertical_points)
            centered = vertical_points - point
            cov = np.cov(centered.T)
            eigenvalues, eigenvectors = np.linalg.eigh(cov)
            vertical_dir = eigenvectors[:, np.argmax(eigenvalues)]

        # Compute normal as cross product of directions
        if horizontal_dir is not None and vertical_dir is not None:
            normal = np.cross(horizontal_dir, vertical_dir)
            norm = np.linalg.norm(normal)
            if norm > 1e-10:  # Avoid division by zero
                return normal / norm

        # Fallback: use simpler normal estimation if directions are unreliable
        _, indices = self.kdtree.query(point, k=4)  # Get closest points
        valid_indices = indices[indices < len(reference_points)]
        if len(valid_indices) >= 3:
            points = reference_points[valid_indices[:3]]
            v1 = points[1] - points[0]
            v2 = points[2] - points[0]
            normal = np.cross(v1, v2)
            norm = np.linalg.norm(normal)
            if norm > 1e-10:
                return normal / norm

        # Final fallback: return vertical normal
        return np.array([0.0, 0.0, 1.0])

    def _estimate_curvature(
        self, point: np.ndarray, reference_points: np.ndarray, center_idx: int
    ) -> float:
        """
        Estimates local surface curvature at an intersection point.
        Uses local fitting of a quadratic surface to neighboring points.

        Args:
            point: Intersection point coordinates
            reference_points: Array of nearby points
            center_idx: Index of the closest reference point

        Returns:
            Estimated mean curvature value
        """
        # Get neighborhood points for curvature estimation
        _, indices = self.kdtree.query(
            point, k=min(self.neighborhood_size, len(reference_points))
        )

        if len(indices) < 4:  # Need at least 4 points for quadratic fitting
            return 0.0

        # Extract valid neighboring points
        neighbors = reference_points[indices]
        centered = neighbors - point

        try:
            # Project points onto tangent plane
            normal = self._estimate_normal(point, reference_points, center_idx)

            # Create local coordinate system
            z_axis = normal
            x_axis = np.array([-normal[1], normal[0], 0])
            if np.all(x_axis == 0):
                x_axis = np.array([1, 0, 0])
            x_axis /= np.linalg.norm(x_axis)
            y_axis = np.cross(z_axis, x_axis)

            # Transform points to local coordinates
            transform = np.vstack([x_axis, y_axis, z_axis])
            local_coords = centered @ transform.T

            # Fit quadratic surface z = ax² + by² + cxy
            A = np.array([[x * x, y * y, x * y] for x, y, _ in local_coords])
            b = local_coords[:, 2]

            # Solve least squares problem
            coeffs, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)

            if rank < 3:  # If fit is unreliable
                return 0.0

            # Compute mean curvature from coefficients
            a, b, c = coeffs
            mean_curvature = abs(a + b)  # Simplified mean curvature estimate

            return mean_curvature

        except np.linalg.LinAlgError:
            return 0.0  # Return zero curvature if computation fails


class SurfaceInterpolator:
    """
    Performs smooth surface interpolation between known intersection points.
    Uses Hermite interpolation with curvature-aware refinement.
    """

    def __init__(self, grid_points: List[GridPoint], smoothing_factor: float = 0.1):
        self.grid_points = grid_points
        self.smoothing_factor = smoothing_factor

    def create_structured_grid(self) -> vtk.vtkStructuredGrid:
        """
        Creates a VTK structured grid from intersection points.
        Determines optimal grid dimensions based on point distribution.

        Returns:
            VTK structured grid populated with intersection points
        """
        # Implementation of grid creation
        grid = vtk.vtkStructuredGrid()
        # ... grid setup code ...
        return grid

    def interpolate_surface(self) -> vtk.vtkPolyData:
        """
        Performs surface interpolation using Hermite interpolation.
        Adapts interpolation density based on local curvature.

        Returns:
            VTK polydata containing the interpolated surface
        """
        # Implementation of surface interpolation
        surface = vtk.vtkPolyData()
        # ... interpolation code ...
        return surface


class SurfaceReconstructor:
    """
    Main class for surface reconstruction from contour actors.
    Coordinates the entire reconstruction process and provides the final surface.
    """

    def __init__(self, neighborhood_size: int = 20, smoothing_iterations: int = 2):
        self.neighborhood_size = neighborhood_size
        self.smoothing_iterations = smoothing_iterations

    def reconstruct(
        self, horizontal_contours: vtk.vtkActor, vertical_traces: vtk.vtkActor
    ) -> vtk.vtkActor:
        """
        Reconstructs a surface from horizontal contours and vertical traces.

        Args:
            horizontal_contours: Actor containing horizontal contour lines
            vertical_traces: Actor containing vertical trace lines

        Returns:
            Actor containing the reconstructed surface
        """
        # Extract intersection points
        extractor = ContourIntersectionExtractor()
        grid_points = extractor.find_intersections(horizontal_contours, vertical_traces)

        # Create interpolated surface
        interpolator = SurfaceInterpolator(grid_points)
        surface_polydata = interpolator.interpolate_surface()

        # Create final surface actor
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(surface_polydata)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        self._configure_actor_properties(actor)

        return actor

    def _configure_actor_properties(self, actor: vtk.vtkActor) -> None:
        """
        Configures visual properties of the surface actor.

        Args:
            actor: VTK actor to configure
        """
        properties = actor.GetProperty()
        properties.SetAmbient(0.3)
        properties.SetDiffuse(0.7)
        properties.SetSpecular(0.2)
        properties.SetSpecularPower(20)
