"""
Example implementation showing how to visualize an arbitrary implicit surface equation.
"""

from rich import print
import sympy as sp
import numpy as np
from sympy import symbols, Eq
from src.core.visualization import setup_renderer, configure_window
from src.core.interactor import CustomInteractorStyle
from src.utils.surface_utils import create_advanced_surface
from src.utils.trace_utils import create_vertical_traces
from src.core.constants import WINDOW_WIDTH, WINDOW_HEIGHT, colors
from src.utils.surface_utils import create_implicit_surface_actor


def main():
    # Setup
    ren, renWin, iren = setup_renderer()
    configure_window(renWin, ren, WINDOW_WIDTH, WINDOW_HEIGHT, "Ellipsoid Example")

    # Set up interactor style
    style = CustomInteractorStyle()
    iren.SetInteractorStyle(style)

    # Define the implicit equation
    x, y, z = symbols("x y z")
    a, b, c = 1, 1, 1
    eq = Eq(x - 0.1, 0)

    # Create the advanced surface
    # surface_actor, trace_collection = create_advanced_surface(
    #     eq,
    #     x_range=(-2, 2),
    #     y_range=(-2, 2),
    #     visualization_scheme={
    #         "type": "basic",
    #         "colors": ["#008080", "#FF8C00"],
    #         "material": {
    #             "ambient": 0.3,
    #             "diffuse": 0.8,
    #             "specular": 0.5,
    #             "power": 20,
    #             "metallic": False,
    #             "roughness": 0.5,
    #         },
    #         "traces": False,
    #         "trace_settings": {
    #             "x_traces": True,
    #             "y_traces": True,
    #             "spacing": 0.5,
    #             "color": [0.5, 0.5, 0.5],
    #             "opacity": 0.7,
    #             "line_style": {
    #                 "width": 2,
    #                 "pattern": "dashed",
    #                 "dash_length": 10,
    #                 "dot_spacing": 5,
    #             },
    #         },
    #     },
    # )

    def equation(x, y, z):
        return x**2 + y**2 + z**2 - 1

    surface_actor = create_implicit_surface_actor(equation)

    # Add the surface and traces to the renderer
    ren.AddActor(surface_actor)
    # for trace_actor in trace_collection:
    # ren.AddActor(trace_actor)

    # Initialize and start
    iren.Initialize()
    ren.ResetCamera()
    ren.GetActiveCamera().Zoom(1.5)
    renWin.Render()
    iren.Start()


if __name__ == "__main__":
    main()
