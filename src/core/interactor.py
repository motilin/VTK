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