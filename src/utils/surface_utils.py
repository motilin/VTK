import sympy as sp
import numpy as np
import vtk
from src.core.constants import COLORS, X_MIN, X_MAX, Y_MIN, Y_MAX, Z_MIN, Z_MAX


def create_func_surface_actor(
    implicit_function,
    bounds=(X_MIN, X_MAX, Y_MIN, Y_MAX, Z_MIN, Z_MAX),
    sample_dims=(100, 100, 100),
    iso_value=0.0,
):
    """
    Creates a VTK actor for an implicit surface defined by a function f(x,y,z).

    Parameters:
    -----------
    implicit_function : callable
        A function that takes three numpy arrays (x,y,z) and returns scalar values.
        The surface will be extracted where these values equal iso_value.
    bounds : tuple
        (xmin, xmax, ymin, ymax, zmin, zmax) defining the volume to sample
    sample_dims : tuple
        Number of samples in each dimension (nx, ny, nz)
    iso_value : float
        The value at which to extract the isosurface

    Returns:
    --------
    vtk.vtkActor
        Actor containing the surface representation
    """
    # Create a structured grid of points
    x = np.linspace(bounds[0], bounds[1], sample_dims[0])
    y = np.linspace(bounds[2], bounds[3], sample_dims[1])
    z = np.linspace(bounds[4], bounds[5], sample_dims[2])

    # Create 3D coordinate arrays
    X, Y, Z = np.meshgrid(x, y, z, indexing="ij")

    # Evaluate the implicit function
    try:
        scalars = implicit_function(X, Y, Z)
    except Exception as e:
        print(f"Error: {e}")
        return vtk.vtkActor()

    if not isinstance(scalars, np.ndarray):
        return vtk.vtkActor()

    # Create VTK structured points dataset
    volume = vtk.vtkStructuredPoints()
    volume.SetDimensions(sample_dims)
    volume.SetOrigin(bounds[0], bounds[2], bounds[4])
    volume.SetSpacing(
        (bounds[1] - bounds[0]) / (sample_dims[0] - 1),
        (bounds[3] - bounds[2]) / (sample_dims[1] - 1),
        (bounds[5] - bounds[4]) / (sample_dims[2] - 1),
    )

    # Add the scalar values to the dataset
    scalar_array = vtk.vtkDoubleArray()
    scalar_array.SetNumberOfComponents(1)
    scalar_array.SetNumberOfValues(np.prod(sample_dims))
    for i, val in enumerate(scalars.flatten(order="F")):  # VTK uses Fortran ordering
        scalar_array.SetValue(i, val)
    volume.GetPointData().SetScalars(scalar_array)

    # Create the contour filter
    contours = vtk.vtkContourFilter()
    contours.SetInputData(volume)
    contours.SetValue(0, iso_value)
    contours.Update()

    contour_output = contours.GetOutput()
    if contour_output.GetNumberOfPoints() == 0:
        return vtk.vtkActor()

    # Optional: Add smoothing for better visual quality
    smoother = vtk.vtkWindowedSincPolyDataFilter()
    smoother.SetInputConnection(contours.GetOutputPort())
    smoother.SetNumberOfIterations(15)
    smoother.SetFeatureEdgeSmoothing(False)
    smoother.SetFeatureAngle(120.0)
    smoother.SetEdgeAngle(90.0)
    smoother.SetPassBand(0.1)
    smoother.NonManifoldSmoothingOn()
    smoother.NormalizeCoordinatesOn()
    smoother.Update()

    # Create mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(smoother.GetOutputPort())
    mapper.ScalarVisibilityOff()

    # Create actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    return actor


def set_z_gradient_coloring(actor, color1=(1, 0, 0), color2=(0, 0, 1), opacity=1.0):
    """
    Adds a gradient coloring to a VTK actor based on z-coordinate values.

    Parameters:
    -----------
    actor : vtk.vtkActor
        The VTK actor to modify
    color1 : tuple
        RGB values (0-1) for the lowest z-coordinate
    color2 : tuple
        RGB values (0-1) for the highest z-coordinate
    opacity : float
        Opacity value (0-1) for the actor
    """
    # Get the mapper and ensure the pipeline is updated
    mapper = actor.GetMapper()
    if not mapper:
        return actor
    mapper.Update()

    # Get the polydata after pipeline execution
    polydata = mapper.GetInput()
    if not polydata:
        # If still None, try getting it from the algorithm output
        polydata = mapper.GetInputConnection(0).GetProducer().GetOutput()
        polydata.Update()

    # Now get points after ensuring pipeline execution
    points = polydata.GetPoints()
    if not points:
        return actor

    # Get number of points
    n_points = points.GetNumberOfPoints()

    # Create array for colors
    colors = vtk.vtkUnsignedCharArray()
    colors.SetNumberOfComponents(4)  # RGBA
    colors.SetName("Colors")

    # Find z-coordinate range
    z_min = float("inf")
    z_max = float("-inf")

    for i in range(n_points):
        point = points.GetPoint(i)
        z = point[2]
        z_min = min(z_min, z)
        z_max = max(z_max, z)

    # Avoid division by zero if surface is flat
    z_range = z_max - z_min
    if z_range == 0:
        z_range = 1

    # Assign colors based on z-coordinate
    for i in range(n_points):
        point = points.GetPoint(i)
        z = point[2]

        # Calculate normalized position (0 to 1)
        t = (z - z_min) / z_range

        # Interpolate colors
        try:
            r = int((color1[0] * (1 - t) + color2[0] * t) * 255)
            g = int((color1[1] * (1 - t) + color2[1] * t) * 255)
            b = int((color1[2] * (1 - t) + color2[2] * t) * 255)
            a = int(opacity * 255)
        except Exception as e:
            print(f"Error in color interpolation: {e}")
            # color.InsertNextTuple4 a transparent color
            colors.InsertNextTuple4(0, 0, 0, 0)
            continue

        colors.InsertNextTuple4(r, g, b, a)

    # Add the colors to the polydata
    polydata.GetPointData().SetScalars(colors)

    # Update the mapper
    mapper.SetScalarVisibility(1)
    mapper.Update()

    return actor


def create_parametric_func_surface_actor(
    parametric_function,
    u_range=(0, 1),
    v_range=(0, 1),
    global_bounds=(X_MIN, X_MAX, Y_MIN, Y_MAX, Z_MIN, Z_MAX),
    color1=(1, 0, 0),
    color2=(0, 0, 1),
    opacity=1.0,
    min_samples=20,
    max_samples=100,
):
    """
    Creates a VTK actor for a parametric surface with controlled cell connectivity.

    Parameters:
        parametric_function: Function that takes (U, V) and returns (X, Y, Z)
        u_range, v_range: Tuple of (min, max) for parameters
        global_bounds: Tuple of (x_min, x_max, y_min, y_max, z_min, z_max)
        color1, color2: RGB tuples for gradient coloring
        opacity: Surface opacity (0 to 1)
        min_samples: Minimum number of samples per dimension
        max_samples: Maximum number of samples per dimension
    """

    def estimate_sampling_density(
        func, param_range, other_range, is_u=True, test_samples=100
    ):
        """Estimate required sampling density based on function variation"""
        p = np.linspace(param_range[0], param_range[1], test_samples)
        dp = (param_range[1] - param_range[0]) / (test_samples - 1)

        test_vals_x = np.zeros(test_samples)
        test_vals_y = np.zeros(test_samples)
        test_vals_z = np.zeros(test_samples)

        other_mid = (other_range[0] + other_range[1]) / 2

        for i, pi in enumerate(p):
            if is_u:
                U, V = np.meshgrid([pi], [other_mid])
            else:
                U, V = np.meshgrid([other_mid], [pi])

            X, Y, Z = func(U, V)
            test_vals_x[i] = X.flatten()[0]
            test_vals_y[i] = Y.flatten()[0]
            test_vals_z[i] = Z.flatten()[0]

        test_vals = np.vstack((test_vals_x, test_vals_y, test_vals_z)).T

        # Calculate numerical derivatives
        derivatives = np.diff(test_vals, axis=0) / dp

        # Calculate curvature using finite differences
        second_derivatives = np.diff(derivatives, axis=0) / dp

        # Estimate required samples based on maximum curvature
        max_curvature = np.max(np.abs(second_derivatives))

        if max_curvature < 1e-6:
            return min_samples

        suggested_samples = int(
            np.sqrt(max_curvature) * (max_samples - min_samples) + min_samples
        )
        return min(max_samples, max(min_samples, suggested_samples))

    # Determine adaptive sampling for each dimension
    u_samples = estimate_sampling_density(
        parametric_function, u_range, v_range, is_u=True
    )
    v_samples = estimate_sampling_density(
        parametric_function, v_range, u_range, is_u=False
    )

    # Create parametric coordinate grids with adaptive sampling
    u = np.linspace(u_range[0], u_range[1], u_samples)
    v = np.linspace(v_range[0], v_range[1], v_samples)
    U, V = np.meshgrid(u, v, indexing="ij")

    # Evaluate the parametric function
    try:
        X, Y, Z = parametric_function(U, V)
    except Exception as e:
        print(f"Error in parametric function evaluation: {e}")
        return vtk.vtkActor()

    # Validate output
    if not (X.shape == Y.shape == Z.shape == U.shape):
        raise ValueError(
            "Parametric function must return x, y, z arrays of same shape as input"
        )

    # Global bounds filtering
    x_min, x_max, y_min, y_max, z_min, z_max = global_bounds
    mask = (
        (X >= x_min)
        & (X <= x_max)
        & (Y >= y_min)
        & (Y <= y_max)
        & (Z >= z_min)
        & (Z <= z_max)
    )

    # Create polydata
    polydata = vtk.vtkPolyData()
    points = vtk.vtkPoints()
    cells = vtk.vtkCellArray()

    # Create colors array
    colors = vtk.vtkUnsignedCharArray()
    colors.SetNumberOfComponents(4)
    colors.SetName("Colors")

    # Find z range for color mapping
    z_min = np.min(Z[mask]) if np.any(mask) else np.min(Z)
    z_max = np.max(Z[mask]) if np.any(mask) else np.max(Z)
    z_range = z_max - z_min if z_max > z_min else 1.0

    # Create point to index mapping
    point_indices = -np.ones((u_samples, v_samples), dtype=int)
    current_index = 0

    # First pass: add points and store their indices
    for i in range(u_samples):
        for j in range(v_samples):
            if mask[i, j]:
                x, y, z = X[i, j], Y[i, j], Z[i, j]
                points.InsertNextPoint(x, y, z)

                # Calculate color based on z-value
                t = (z - z_min) / z_range if z_range > 0 else 0.5
                r = int((color1[0] * (1 - t) + color2[0] * t) * 255)
                g = int((color1[1] * (1 - t) + color2[1] * t) * 255)
                b = int((color1[2] * (1 - t) + color2[2] * t) * 255)
                a = int(opacity * 255)
                colors.InsertNextTuple4(r, g, b, a)

                point_indices[i, j] = current_index
                current_index += 1

    # Second pass: create quad cells
    for i in range(u_samples - 1):
        for j in range(v_samples - 1):
            # Get indices for the four corners of the quad
            idx00 = point_indices[i, j]
            idx10 = point_indices[i + 1, j]
            idx01 = point_indices[i, j + 1]
            idx11 = point_indices[i + 1, j + 1]

            # Only create cell if all points are valid and at least one point is in bounds
            if idx00 >= 0 and idx10 >= 0 and idx01 >= 0 and idx11 >= 0:
                # Check if points are within a reasonable distance
                p00 = np.array([X[i, j], Y[i, j], Z[i, j]])
                p10 = np.array([X[i + 1, j], Y[i + 1, j], Z[i + 1, j]])
                p01 = np.array([X[i, j + 1], Y[i, j + 1], Z[i, j + 1]])
                p11 = np.array([X[i + 1, j + 1], Y[i + 1, j + 1], Z[i + 1, j + 1]])

                # Calculate edge lengths
                d1 = np.linalg.norm(p10 - p00)
                d2 = np.linalg.norm(p01 - p00)
                d3 = np.linalg.norm(p11 - p10)
                d4 = np.linalg.norm(p11 - p01)

                # Calculate average edge length
                avg_edge = (d1 + d2 + d3 + d4) / 4
                max_edge = max(d1, d2, d3, d4)

                # Only create quad if edges are reasonably similar in length
                if max_edge < 3 * avg_edge:
                    quad = vtk.vtkQuad()
                    quad.GetPointIds().SetId(0, idx00)
                    quad.GetPointIds().SetId(1, idx10)
                    quad.GetPointIds().SetId(2, idx11)
                    quad.GetPointIds().SetId(3, idx01)
                    cells.InsertNextCell(quad)

    # Set the points and cells in the polydata
    polydata.SetPoints(points)
    polydata.SetPolys(cells)
    polydata.GetPointData().SetScalars(colors)

    # Create mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(polydata)
    mapper.SetScalarVisibility(1)

    # Create actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    return actor


def create_point_actor(
    coordinates,  # Point coordinates (x, y, z)
    color=COLORS.GetColor3d("charcoal"),  # Actor color
    thickness=1.0,  # Sphere thickness
    opacity=1.0,  # Actor opacity
    global_bounds=None,  # Global bounds for clipping
):
    if global_bounds:
        x_min, x_max, y_min, y_max, z_min, z_max = global_bounds
        if not (x_min <= coordinates[0] <= x_max):
            return None
        if not (y_min <= coordinates[1] <= y_max):
            return None
        if not (z_min <= coordinates[2] <= z_max):
            return None

    radius = thickness / 20

    # Create sphere source
    sphere = vtk.vtkSphereSource()
    sphere.SetCenter(coordinates)
    sphere.SetRadius(radius)
    sphere.SetPhiResolution(24)
    sphere.SetThetaResolution(24)

    # Create mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(sphere.GetOutputPort())

    # Create an actor for the sphere
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)
    actor.GetProperty().SetOpacity(opacity)
    actor.GetProperty().SetAmbient(0.3)
    actor.GetProperty().SetDiffuse(0.7)
    actor.GetProperty().SetSpecular(0.2)
    actor.GetProperty().SetSpecularPower(20)

    return actor
