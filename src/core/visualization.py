# src/core/visualization.py
"""
Core visualization functionality.
"""
import vtk
from .constants import COLORS, DEFAULT_BACKGROUND_COLOR
from src.core.interactor import CustomInteractorStyle


def setup_renderer():
    """Set up the basic rendering environment."""
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    # Set up interactor style
    # style = CustomInteractorStyle()
    # iren.SetInteractorStyle(style)

    return ren, renWin, iren


def configure_window(renWin, ren, width, height):
    """Configure the render window."""
    ren.SetBackground(DEFAULT_BACKGROUND_COLOR)
    renWin.SetSize(width, height)
