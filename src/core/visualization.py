# src/core/visualization.py
"""
Core visualization functionality.
"""
import vtk
from .constants import colors


def setup_renderer():
    """Set up the basic rendering environment."""
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    return ren, renWin, iren


def configure_window(renWin, ren, width, height, title):
    """Configure the render window."""
    ren.SetBackground(colors.GetColor3d("dark_blue"))
    renWin.SetSize(width, height)
    renWin.SetWindowName(title)
