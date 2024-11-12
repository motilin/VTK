"""
Utilities for creating and managing trace lines.
"""

import vtk
import numpy as np


def create_vertical_traces(
    eq, constant_axis, x_range, y_range, spacing, color, opacity, line_style
):
    """
    Create vertical trace planes for a given constant axis with customizable line styles

    Parameters:
    -----------
    eq : sympy.Equation
        The surface equation
    constant_axis : str
        'x' or 'y' to indicate which axis to hold constant
    spacing : float
        Distance between trace planes
    line_style : dict
        Dictionary containing line style parameters
    """
    traces = []

    if constant_axis == "x":
        range_vals = np.arange(x_range[0], x_range[1] + spacing, spacing)
        var_range = np.linspace(y_range[0], y_range[1], 50)
    else:  # y-constant
        range_vals = np.arange(y_range[0], y_range[1] + spacing, spacing)
        var_range = np.linspace(x_range[0], x_range[1], 50)

    for k in range_vals:
        points = vtk.vtkPoints()
        lines = vtk.vtkCellArray()

        # Calculate points along the trace
        valid_points = []
        for t in var_range:
            if constant_axis == "x":
                x_val, y_val = k, t
            else:
                x_val, y_val = t, k

            try:
                z_val = solve_for_z(eq, x_val, y_val)
                valid_points.append((x_val, y_val, z_val))
            except:
                continue

        # Create line segments based on line style
        pattern = line_style.get("pattern", "solid")
        if pattern == "solid":
            create_solid_line(points, lines, valid_points)
        elif pattern == "dashed":
            dash_length = line_style.get("dash_length", 10)
            create_dashed_line(points, lines, valid_points, dash_length)
        elif pattern == "dotted":
            dot_spacing = line_style.get("dot_spacing", 5)
            create_dotted_line(points, lines, valid_points, dot_spacing)

        # Create the trace plane
        trace_data = vtk.vtkPolyData()
        trace_data.SetPoints(points)
        trace_data.SetLines(lines)

        # Create mapper and actor
        trace_mapper = vtk.vtkPolyDataMapper()
        trace_mapper.SetInputData(trace_data)

        trace_actor = vtk.vtkActor()
        trace_actor.SetMapper(trace_mapper)
        trace_actor.GetProperty().SetColor(color)
        trace_actor.GetProperty().SetOpacity(opacity)
        trace_actor.GetProperty().SetLineWidth(line_style.get("width", 2))

        traces.append(trace_actor)

    return traces


def create_solid_line(points, lines, valid_points):
    """Create a solid line from points"""
    for i, point in enumerate(valid_points):
        point_id = points.InsertNextPoint(point)
        if i > 0:
            line = vtk.vtkLine()
            line.GetPointIds().SetId(0, point_id - 1)
            line.GetPointIds().SetId(1, point_id)
            lines.InsertNextCell(line)


def create_dashed_line(points, lines, valid_points, dash_length):
    """Create a dashed line with specified dash length"""
    current_length = 0
    drawing = True

    for i in range(len(valid_points) - 1):
        p1 = valid_points[i]
        p2 = valid_points[i + 1]

        # Calculate segment length
        segment_length = np.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2)))

        if drawing:
            point_id1 = points.InsertNextPoint(p1)
            point_id2 = points.InsertNextPoint(p2)
            line = vtk.vtkLine()
            line.GetPointIds().SetId(0, point_id1)
            line.GetPointIds().SetId(1, point_id2)
            lines.InsertNextCell(line)

        current_length += segment_length
        if current_length >= dash_length:
            current_length = 0
            drawing = not drawing


def create_dotted_line(points, lines, valid_points, dot_spacing):
    """Create a dotted line with specified spacing"""
    current_length = 0

    for i in range(len(valid_points)):
        current_length += dot_spacing if i > 0 else 0

        if current_length >= dot_spacing:
            point_id = points.InsertNextPoint(valid_points[i])
            point = vtk.vtkVertex()
            point.GetPointIds().SetId(0, point_id)
            lines.InsertNextCell(point)
            current_length = 0
