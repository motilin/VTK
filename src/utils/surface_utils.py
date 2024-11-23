import sympy as sp
import numpy as np
import vtk
from src.core.constants import COLORS


def create_func_surface_actor(
    implicit_function,
    bounds=(-10, 10, -10, 10, -10, 10),
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
        r = int((color1[0] * (1 - t) + color2[0] * t) * 255)
        g = int((color1[1] * (1 - t) + color2[1] * t) * 255)
        b = int((color1[2] * (1 - t) + color2[2] * t) * 255)
        a = int(opacity * 255)

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
    global_bounds=(-10, 10, -10, 10, -10, 10),
    color1=(1, 0, 0),
    color2=(0, 0, 1),
    opacity=1.0,
    sample_dims=(100, 100),
):
    """
    Creates a VTK actor for a parametric surface with global bounds clipping and z-gradient coloring.

    Parameters are same as previous implementation.
    """
    # Create parametric coordinate grids
    u = np.linspace(u_range[0], u_range[1], sample_dims[0])
    v = np.linspace(v_range[0], v_range[1], sample_dims[1])
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

    # Create masks for points within global bounds
    mask = (
        (X >= x_min)
        & (X <= x_max)
        & (Y >= y_min)
        & (Y <= y_max)
        & (Z >= z_min)
        & (Z <= z_max)
    )

    # Filter coordinates
    X_filtered = X[mask]
    Y_filtered = Y[mask]
    Z_filtered = Z[mask]

    # Create VTK points
    points = vtk.vtkPoints()

    # Prepare point data
    point_data = vtk.vtkDoubleArray()
    point_data.SetNumberOfComponents(1)
    point_data.SetName("Z")

    # Add filtered points and z values
    for x, y, z in zip(X_filtered, Y_filtered, Z_filtered):
        points.InsertNextPoint(x, y, z)
        point_data.InsertNextValue(z)

    # Create polydata
    poly_data = vtk.vtkPolyData()
    poly_data.SetPoints(points)

    # Create surface using Delaunay triangulation
    delaunay = vtk.vtkDelaunay2D()
    delaunay.SetInputData(poly_data)
    delaunay.Update()

    # Get the triangulated surface
    surface = delaunay.GetOutput()
    surface.GetPointData().SetScalars(point_data)

    # Create mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(surface)

    # Create actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # Determine actual z range for coloring
    actual_z_min = np.min(Z_filtered)
    actual_z_max = np.max(Z_filtered)

    # Prepare color array
    colors = vtk.vtkUnsignedCharArray()
    colors.SetNumberOfComponents(4)  # RGBA
    colors.SetName("Colors")

    # Compute colors based on z values
    for i in range(surface.GetNumberOfPoints()):
        z = surface.GetPoint(i)[2]

        # Calculate normalized position (0 to 1) based on actual z range
        t = (
            (z - actual_z_min) / (actual_z_max - actual_z_min)
            if actual_z_max > actual_z_min
            else 0.5
        )

        # Interpolate colors
        r = int((color1[0] * (1 - t) + color2[0] * t) * 255)
        g = int((color1[1] * (1 - t) + color2[1] * t) * 255)
        b = int((color1[2] * (1 - t) + color2[2] * t) * 255)
        a = int(opacity * 255)

        colors.InsertNextTuple4(r, g, b, a)

    # Add colors to surface
    surface.GetPointData().SetScalars(colors)

    # Update mapper
    mapper.SetScalarVisibility(1)
    mapper.Update()

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