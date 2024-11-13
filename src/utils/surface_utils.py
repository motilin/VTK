import sympy as sp
import numpy as np
import vtk
from src.core.constants import colors
import math


def create_implicit_surface_actor(
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
    scalars = implicit_function(X, Y, Z)

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

    # Create mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(smoother.GetOutputPort())
    mapper.ScalarVisibilityOff()

    # Create actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    return actor


def set_z_gradient_coloring(actor, color1=(1, 0, 0), color2=(0, 0, 1)):
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
    """
    # Get the mapper and ensure the pipeline is updated
    mapper = actor.GetMapper()
    mapper.Update()

    # Get the polydata after pipeline execution
    polydata = mapper.GetInput()
    if not polydata:
        # If still None, try getting it from the algorithm output
        polydata = mapper.GetInputConnection(0).GetProducer().GetOutput()
        polydata.Update()

    # Now get points after ensuring pipeline execution
    points = polydata.GetPoints()
    n_points = points.GetNumberOfPoints()

    # Create array for colors
    colors = vtk.vtkUnsignedCharArray()
    colors.SetNumberOfComponents(3)
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

        colors.InsertNextTuple3(r, g, b)

    # Add the colors to the polydata
    polydata.GetPointData().SetScalars(colors)

    # Update the mapper
    mapper.SetScalarVisibility(1)
    mapper.Update()

    return actor
