import sympy as sp
import numpy as np
import vtk
from src.core.constants import colors
import math

import vtk
import numpy as np


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


def create_main_surface(eq, x_range, y_range, visualization_scheme):
    """
    Create the main surface actor based on the implicit equation with improved error handling.
    """
    # Initialize VTK objects
    points = vtk.vtkPoints()
    triangles = vtk.vtkCellArray()
    valid_points = []  # Keep track of valid point indices
    point_map = {}  # Map (x,y) to point indices

    # Create a grid of points
    x_points = np.linspace(x_range[0], x_range[1], 50)
    y_points = np.linspace(y_range[0], y_range[1], 50)

    # Extract coefficients once
    coefficients = extract_coefficients(eq)

    # First pass: collect valid points
    point_index = 0
    for i, x_val in enumerate(x_points):
        for j, y_val in enumerate(y_points):
            try:
                z_vals = solve_for_z(coefficients, x_val, y_val)
                if z_vals:  # Only process if we got valid z values
                    for z_val in z_vals:
                        if (
                            isinstance(z_val, (int, float))
                            and not np.isnan(z_val)
                            and np.isfinite(z_val)
                        ):
                            points.InsertNextPoint(x_val, y_val, z_val)
                            valid_points.append((i, j))
                            key = (i, j)
                            if key not in point_map:
                                point_map[key] = []
                            point_map[key].append(point_index)
                            point_index += 1
            except (ValueError, ZeroDivisionError):
                continue

    # Safety check
    if points.GetNumberOfPoints() == 0:
        raise ValueError("No valid points generated for the surface")

    # Second pass: create triangles only between valid points
    for i in range(len(x_points) - 1):
        for j in range(len(y_points) - 1):
            # Check if we have all needed points for triangulation
            corners = [(i, j), (i + 1, j), (i, j + 1), (i + 1, j + 1)]
            if all(corner in point_map for corner in corners):
                # Create triangles for each valid combination of z-values
                for p1 in point_map[corners[0]]:
                    for p2 in point_map[corners[1]]:
                        for p3 in point_map[corners[2]]:
                            triangle = vtk.vtkTriangle()
                            triangle.GetPointIds().SetId(0, p1)
                            triangle.GetPointIds().SetId(1, p2)
                            triangle.GetPointIds().SetId(2, p3)
                            triangles.InsertNextCell(triangle)

                        for p4 in point_map[corners[3]]:
                            triangle = vtk.vtkTriangle()
                            triangle.GetPointIds().SetId(0, p2)
                            triangle.GetPointIds().SetId(1, p4)
                            triangle.GetPointIds().SetId(2, p3)
                            triangles.InsertNextCell(triangle)

    # Create the polydata
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    polydata.SetPolys(triangles)

    # Clean the polydata to remove any unused points or degenerate cells
    cleaner = vtk.vtkCleanPolyData()
    cleaner.SetInputData(polydata)
    cleaner.Update()

    # Triangulate any non-triangular polygons
    triangulator = vtk.vtkTriangleFilter()
    triangulator.SetInputConnection(cleaner.GetOutputPort())
    triangulator.Update()

    # Create normals
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputConnection(triangulator.GetOutputPort())
    normals.SetFeatureAngle(60.0)
    normals.Update()

    # Create the mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(normals.GetOutputPort())
    mapper.ScalarVisibilityOff()

    # Create the actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # Set appearance properties
    actor.GetProperty().SetColor(colors.GetColor3d("#008080"))
    if visualization_scheme:
        material = visualization_scheme.get("material", {})
        actor.GetProperty().SetAmbient(material.get("ambient", 0.3))
        actor.GetProperty().SetDiffuse(material.get("diffuse", 0.8))
        actor.GetProperty().SetSpecular(material.get("specular", 0.5))
        actor.GetProperty().SetSpecularPower(material.get("power", 20))

    return actor


def create_advanced_surface(
    eq, x_range=(-2, 2), y_range=(-2, 2), visualization_scheme=None
):
    """
    Create an advanced surface with error handling and safety checks.
    """
    try:
        # Create default visualization scheme if none provided
        if visualization_scheme is None:
            visualization_scheme = {
                "type": "basic",
                "colors": ["#008080", "#FF8C00"],
                "material": {
                    "ambient": 0.3,
                    "diffuse": 0.8,
                    "specular": 0.5,
                    "power": 20,
                    "metallic": False,
                    "roughness": 0.5,
                },
                "traces": False,
                "trace_settings": {
                    "x_traces": True,
                    "y_traces": True,
                    "spacing": 0.5,
                    "color": [0.5, 0.5, 0.5],
                    "opacity": 0.7,
                    "line_style": {
                        "width": 2,
                        "pattern": "dashed",
                        "dash_length": 10,
                        "dot_spacing": 5,
                    },
                },
            }

        # Validate ranges
        if not (
            isinstance(x_range, tuple)
            and len(x_range) == 2
            and isinstance(y_range, tuple)
            and len(y_range) == 2
        ):
            raise ValueError("Invalid range specifications")

        # Create the main surface
        surface_actor = create_main_surface(eq, x_range, y_range, visualization_scheme)

        return (
            surface_actor,
            [],
        )  # Return empty trace collection since traces are disabled

    except Exception as e:
        print(f"Error creating surface: {str(e)}")
        raise


def extract_coefficients(eq):
    """
    Extracts the coefficients A, B, C, D, E, F, G, H, I, J from an equation in expanded form Ax^2 + By^2 + Cz^2 + Dxy + Eyz + Fxz + Gx + Hy + Iz + J = 0.

    Parameters:
    eq (sympy.Eq): The equation to extract the coefficients from

    Returns:
    dict: A dictionary containing the coefficients A, B, C, D, E, F, G, H, I, J
    """

    # Extract the expanded form coefficients
    x, y, z = sp.symbols("x y z")
    expanded = sp.expand(eq.lhs)

    poly = sp.Poly(expanded, x, y, z)

    A = poly.coeff_monomial(x**2)
    B = poly.coeff_monomial(y**2)
    C = poly.coeff_monomial(z**2)
    D = poly.coeff_monomial(x * y)
    E = poly.coeff_monomial(y * z)
    F = poly.coeff_monomial(x * z)
    G = poly.coeff_monomial(x)
    H = poly.coeff_monomial(y)
    I = poly.coeff_monomial(z)
    J = poly.coeff_monomial(1)

    return {
        "A": A,
        "B": B,
        "C": C,
        "D": D,
        "E": E,
        "F": F,
        "G": G,
        "H": H,
        "I": I,
        "J": J,
    }


def solve_for_z(coefficients, x_val, y_val):
    """
    Solve the equation Ax^2 + By^2 + Cz^2 + Dxy + Eyz + Fxz + Gx + Hy + Iz + J = 0 for all real values of z given x and y.

    Parameters:
    coefficients (dict): A dictionary of the form {"A":A, "B":B, "C":C, "D":D, "E":E, "F":F, "G":G, "H":H, "I":I, "J":J} containing the coefficients of the equation
    x_val (float): The value of x
    y_val (float): The value of y

    Returns:
    list: A list of all real solutions for z
    """

    A = coefficients["A"]
    B = coefficients["B"]
    C = coefficients["C"]
    D = coefficients["D"]
    E = coefficients["E"]
    F = coefficients["F"]
    G = coefficients["G"]
    H = coefficients["H"]
    I = coefficients["I"]
    J = coefficients["J"]

    # Coefficients for the quadratic equation in z: az^2 + bz + c = 0
    a = C
    b = E * y_val + F * x_val + I
    c = A * x_val**2 + B * y_val**2 + D * x_val * y_val + G * x_val + H * y_val + J

    # Check if it's a quadratic equation
    if a == 0:
        if b == 0:
            # No z terms at all
            if c == 0:
                # Infinite solutions for z (identity 0 = 0)
                return []
            else:
                # No solution, as the equation is inconsistent
                return []
        else:
            # Linear case bz + c = 0 -> z = -c / b
            return [-c / b]

    # Calculate the discriminant
    discriminant = b**2 - 4 * a * c

    if discriminant < 0:
        # No real solutions
        return []
    elif discriminant == 0:
        # One real solution
        z = -b / (2 * a)
        return [z]
    else:
        # Two real solutions
        sqrt_discriminant = math.sqrt(discriminant)
        z1 = (-b + sqrt_discriminant) / (2 * a)
        z2 = (-b - sqrt_discriminant) / (2 * a)
        return [z1, z2]
