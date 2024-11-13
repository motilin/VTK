# src/core/visualization.py
"""
Core visualization functionality.
"""
import vtk
from .constants import colors
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
    ren.SetBackground(colors.GetColor3d("dark_blue"))
    renWin.SetSize(width, height)


def set_mathematical_view(renderer):
    """
    Sets up the classic mathematical textbook view where:
    - X axis points left
    - Y axis points right
    - Z axis points up
    - XY plane is horizontal
    - View is straight-on to the XZ plane

    Parameters:
    -----------
    renderer : vtkRenderer
        The renderer whose camera will be transformed
    """
    # Get the camera
    camera = renderer.GetActiveCamera()

    # Reset the camera first
    camera.SetPosition(0, 1, 0)  # Position along negative Y axis
    camera.SetViewUp(0, 0, 1)  # Z axis points up
    camera.SetFocalPoint(0, 0, 0)  # Looking at origin

    # Optional: adjust for better initial view
    camera.Elevation(20)  # Slight elevation to see 3D better
    camera.Azimuth(-45)  # Slight rotation to enhance 3D perspective

    # Reset the camera to fit all actors
    renderer.ResetCamera()
