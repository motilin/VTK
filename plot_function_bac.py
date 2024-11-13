import os, sys
from dotenv import load_dotenv

# Dynamically set PYTHONPATH in .env
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.environ["PYTHONPATH"] = project_root
sys.path.append(project_root)

from rich import print
import sympy as sp
import numpy as np
from sympy import symbols, Eq
from src.core.visualization import (
    setup_renderer,
    configure_window,
    set_mathematical_view,
)
from src.core.constants import WINDOW_WIDTH, WINDOW_HEIGHT, colors
from src.utils.surface_utils import create_implicit_surface_actor
from src.utils.surface_utils import set_z_gradient_coloring
from src.utils.line_utils import create_axes
from src.widgets.sliders import get_button, toggle_visibility
import vtk


def main():
    # Setup
    ren, renWin, iren = setup_renderer()
    configure_window(renWin, ren, WINDOW_WIDTH, WINDOW_HEIGHT, "Ellipsoid Example")

    # Add axes
    math_axes = create_axes(length=10)
    ren.AddActor(math_axes)

    # Add actors

    def implicit_equation(x, y, z):
        return x**2 + y**2 - z**2 - 1

    surface_actor = create_implicit_surface_actor(implicit_equation)
    set_z_gradient_coloring(
        surface_actor, colors.GetColor3d("emerald"), colors.GetColor3d("coral")
    )
    ren.AddActor(surface_actor)

    # Initialize and start
    set_mathematical_view(ren)
    iren.Initialize()
    ren.ResetCamera()
    ren.GetActiveCamera().Zoom(1.5)
    renWin.Render()
    iren.Start()


if __name__ == "__main__":
    main()
