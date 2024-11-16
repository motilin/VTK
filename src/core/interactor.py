"""
Custom interactor styles and related functionality.
"""

import vtk
import sys


# Define the custom interactor style
class CustomInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self):
        super().__init__()
        self.AddObserver(vtk.vtkCommand.LeftButtonPressEvent, self.left_button_press_event)
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
            set_mathematical_view(self.GetCurrentRenderer())
            
            
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
