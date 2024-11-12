"""
Utilities for surface creation and manipulation.
"""

import numpy as np
from sympy import solve


def create_advanced_surface(
    eq,
    x_range=(-2, 2),
    y_range=(-2, 2),
    visualization_scheme={
        "type": "basic",  # or 'curvature', 'critical', 'levelset', 'periodic', 'gradient'
        "colors": ["#0000FF", "#FF0000"],
        "material": {
            "ambient": 0.3,
            "diffuse": 0.8,
            "specular": 0.5,
            "power": 20,
            "metallic": False,
            "roughness": 0.5,
        },
        "bands": 10,  # for levelset
        "period": 1.0,  # for periodic
        "traces": False,  # enable vertical traces
        "trace_settings": {
            "x_traces": True,  # enable traces at constant x
            "y_traces": True,  # enable traces at constant y
            "spacing": 0.5,  # spacing between traces
            "color": [0.2, 0.2, 0.2],  # color for traces
            "opacity": 0.7,  # opacity for traces
            "line_style": {
                "width": 2,
                "pattern": "solid",  # 'solid', 'dashed', 'dotted'
                "dash_length": 10,  # for dashed lines
                "dot_spacing": 5,  # for dotted lines
            },
        },
    },
):
    """
    Create surface with advanced visualization options and customizable vertical traces

    Parameters:
    -----------
    visualization_scheme : dict
        Previous parameters plus:
        'traces': Boolean to enable vertical trace planes
        'trace_settings': Dict containing:
            'x_traces': Boolean to enable x-constant traces
            'y_traces': Boolean to enable y-constant traces
            'spacing': Float spacing between trace planes
            'color': RGB color for traces
            'opacity': Opacity for trace planes
            'line_style': Dict containing:
                'width': Line width
                'pattern': 'solid', 'dashed', or 'dotted'
                'dash_length': Length of dashes
                'dot_spacing': Spacing between dots
    """
    # Original surface creation code
    dx = eq.lhs.diff(x)
    dy = eq.lhs.diff(y)
    dz = eq.lhs.diff(z)
    dxx = dx.diff(x)
    dyy = dy.diff(y)
    dxy = dx.diff(y)

    # Create the main surface (previous implementation)
    surface_actor = (
        create_main_surface()
    )  # This would contain the original surface creation code

    # If traces are enabled, create the vertical planes
    if visualization_scheme.get("traces", False):
        trace_collection = vtk.vtkActorCollection()
        trace_settings = visualization_scheme.get("trace_settings", {})

        # Get trace settings with defaults
        x_traces_enabled = trace_settings.get("x_traces", True)
        y_traces_enabled = trace_settings.get("y_traces", True)
        spacing = trace_settings.get("spacing", 0.5)
        trace_color = trace_settings.get("color", [0.2, 0.2, 0.2])
        trace_opacity = trace_settings.get("opacity", 0.7)
        line_style = trace_settings.get(
            "line_style",
            {"width": 2, "pattern": "solid", "dash_length": 10, "dot_spacing": 5},
        )

        # Create x-constant planes if enabled
        if x_traces_enabled:
            x_planes = create_vertical_traces(
                eq,
                "x",
                x_range,
                y_range,
                spacing,
                trace_color,
                trace_opacity,
                line_style,
            )
            for plane in x_planes:
                trace_collection.AddItem(plane)

        # Create y-constant planes if enabled
        if y_traces_enabled:
            y_planes = create_vertical_traces(
                eq,
                "y",
                x_range,
                y_range,
                spacing,
                trace_color,
                trace_opacity,
                line_style,
            )
            for plane in y_planes:
                trace_collection.AddItem(plane)

        return surface_actor, trace_collection

    return surface_actor


def solve_for_z(eq, x_val, y_val):
    """
    Solve the equation for z at a given (x,y) point
    Returns the smallest real z value if multiple solutions exist
    """
    # Substitute x and y values
    eq_at_point = eq.subs([(x, x_val), (y, y_val)])

    # Solve for z
    solutions = solve(eq_at_point, z, dict=True)

    # Get real solutions and return the smallest one
    real_solutions = [float(sol[z].evalf()) for sol in solutions if sol[z].is_real]

    if real_solutions:
        return min(real_solutions)
    raise ValueError("No real solution found")
