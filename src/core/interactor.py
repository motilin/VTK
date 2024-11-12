"""
Custom interactor styles and related functionality.
"""

import vtk
import sys


class CustomInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, parent=None):
        self.AddObserver("KeyPressEvent", self.on_key_press_event)

    def on_key_press_event(self, obj, event):
        key = self.GetInteractor().GetKeySym()
        if key == "q":
            self.GetInteractor().GetRenderWindow().Finalize()
            self.GetInteractor().TerminateApp()
            sys.exit(0)
