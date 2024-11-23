"""
Custom interactor styles and related functionality.
"""

import vtk
import os, sys
from vtk import vtkOBJExporter


# Define the custom interactor style
class CustomInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.AddObserver(
            vtk.vtkCommand.LeftButtonPressEvent, self.left_button_press_event
        )
        # self.AddObserver(vtk.vtkCommand.KeyPressEvent, self.on_key_press_event)

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


def export_to_obj(widget, filepath):
    """
    Exports the current view of the renderer to an OBJ file.

    Parameters:
    -----------
    widget: QWidget
        The widget containing the renderer
    filepath : str
        The complete filepath where the OBJ file should be saved
        (including directory path and filename)
    """
    # Extract directory and basename from the full filepath
    directory = os.path.dirname(filepath)
    basename = os.path.splitext(os.path.basename(filepath))[0]

    # If directory doesn't exist, create it
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    # Construct the full path for the exporter
    # If directory is empty (current directory), just use basename
    file_prefix = os.path.join(directory, basename) if directory else basename

    # Set up and execute the export
    render_window = widget.interactor.GetRenderWindow()
    exporter = vtkOBJExporter()
    exporter.SetFilePrefix(file_prefix)
    exporter.SetInput(render_window)
    exporter.Write()


def export_to_png(widget, filepath):
    """
    Exports the current view of the renderer to a PNG file.

    Parameters:
    -----------
    widget: QWidget
        The widget containing the renderer
    filepath : str
        The complete filepath where the PNG file should be saved
        (including directory path and filename)
    """
    # Ensure the directory exists
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    # If the filepath doesn't end in .png, add it
    if not filepath.lower().endswith(".png"):
        filepath += ".png"

    # Set up and execute the export
    render_window = widget.interactor.GetRenderWindow()
    window_to_image_filter = vtk.vtkWindowToImageFilter()
    window_to_image_filter.SetInput(render_window)
    window_to_image_filter.Update()

    writer = vtk.vtkPNGWriter()
    writer.SetFileName(filepath)
    writer.SetInputConnection(window_to_image_filter.GetOutputPort())
    writer.Write()


def save_state(main_widget, filepath):
    """
    Saves the current state of the main widget to a file.
    """
    pass


def load_state(main_widget, filepath):
    """
    Loads the state of the main widget from a file.
    """
    pass
