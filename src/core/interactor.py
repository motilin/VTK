"""
Custom interactor styles and related functionality.
"""

import vtk
import sys
from vtk import vtkOBJExporter


# Define the custom interactor style
class CustomInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.AddObserver(
            vtk.vtkCommand.LeftButtonPressEvent, self.left_button_press_event
        )
        self.AddObserver(vtk.vtkCommand.KeyPressEvent, self.on_key_press_event)

    def left_button_press_event(self, obj, event):
        self.OnLeftButtonDown()
        return

    def on_key_press_event(self, obj, event):
        key = self.GetInteractor().GetKeySym()
        if key == "q":
            self.GetInteractor().GetRenderWindow().Finalize()
            self.GetInteractor().TerminateApp()
            sys.exit(0)
        if key == "r":
            set_mathematical_view(self.widget.renderer)
        if key == "o":
            export_to_obj(self.widget, "output")
        if key == "p":
            export_to_png(self.widget, "output")


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


def export_to_obj(widget, filename):
    """
    Exports the current view of the renderer to an OBJ file.

    Parameters:
    -----------
    widget: QWidget
        The widget containing the renderer
    filename : str
        The name of the OBJ file to save
    """
    render_window = widget.interactor.GetRenderWindow()
    exporter = vtkOBJExporter()
    exporter.SetFilePrefix(filename)
    exporter.SetInput(render_window)
    exporter.Write()


def export_to_png(widget, filename):
    """
    Exports the current view of the renderer to a PNG file.

    Parameters:
    -----------
    widget: QWidget
        The widget containing the renderer
    filename : str
        The name of the PNG file to save
    """
    render_window = widget.interactor.GetRenderWindow()
    window_to_image_filter = vtk.vtkWindowToImageFilter()
    window_to_image_filter.SetInput(render_window)
    window_to_image_filter.Update()

    writer = vtk.vtkPNGWriter()
    writer.SetFileName(filename + ".png")
    writer.SetInputConnection(window_to_image_filter.GetOutputPort())
    writer.Write()
