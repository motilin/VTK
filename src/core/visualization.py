# src/core/visualization.py
"""
Core visualization functionality.
"""
import vtk
from .constants import COLORS
from src.core.interactor import CustomInteractorStyle


def setup_renderer():
    """Set up the basic rendering environment."""
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    # Set up interactor style
    style = CustomInteractorStyle()
    iren.SetInteractorStyle(style)

    return ren, renWin, iren


def configure_window(renWin, ren, width, height):
    """Configure the render window."""
    ren.SetBackground(COLORS.GetColor3d("dark_blue"))
    renWin.SetSize(width, height)
