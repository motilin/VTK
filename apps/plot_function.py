import os
import sys

# Dynamically set PYTHONPATH in .env
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.environ["PYTHONPATH"] = project_root
sys.path.append(project_root)

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from src.core.visualization import configure_window, set_mathematical_view
from src.core.constants import WINDOW_WIDTH, WINDOW_HEIGHT, colors
from src.utils.surface_utils import (
    create_implicit_surface_actor,
    set_z_gradient_coloring,
)
from src.utils.line_utils import create_axes


# Define the custom interactor style
class CustomInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, parent=None):
        self.AddObserver("LeftButtonPressEvent", self.left_button_press_event)

    def left_button_press_event(self, obj, event):
        self.OnLeftButtonDown()
        return


class VTKWidget(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main widget and layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Create the VTK render window interactor
        self.vtk_widget = QVTKRenderWindowInteractor(self.central_widget)
        self.layout.addWidget(self.vtk_widget)

        # Create the button
        self.toggle_button = QPushButton("Toggle Axes Visibility", self)
        self.toggle_button.clicked.connect(self.toggle_visibility)
        self.layout.addWidget(self.toggle_button)

        # Set up the VTK renderer and window
        self.renderer = vtk.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        self.interactor = self.vtk_widget.GetRenderWindow().GetInteractor()

        # Setup renderer and window
        configure_window(
            self.vtk_widget.GetRenderWindow(),
            self.renderer,
            WINDOW_WIDTH,
            WINDOW_HEIGHT,
            "Function Plotter",
        )

        # Add axes
        self.math_axes = create_axes(length=10)
        self.renderer.AddActor(self.math_axes)

        # Add actors
        def implicit_equation(x, y, z):
            return x**2 + y**2 - z**2 - 1

        surface_actor = create_implicit_surface_actor(implicit_equation)
        set_z_gradient_coloring(
            surface_actor, colors.GetColor3d("emerald"), colors.GetColor3d("coral")
        )
        self.renderer.AddActor(surface_actor)

        # Initialize visibility state
        self.axes_visible = True

        # Initialize the interactor
        set_mathematical_view(self.renderer)
        self.vtk_widget.GetRenderWindow().Render()
        self.interactor.Initialize()

        # Set up interactor style
        style = CustomInteractorStyle()
        self.interactor.SetInteractorStyle(style)

        # Set initial size of the window
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

    def toggle_visibility(self):
        # Toggle the visibility of the axes actor
        self.axes_visible = not self.axes_visible
        self.math_axes.SetVisibility(self.axes_visible)
        self.vtk_widget.GetRenderWindow().Render()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VTKWidget()
    window.setWindowTitle("VTK Shape in Qt with Axes Visibility Toggle")
    window.show()
    sys.exit(app.exec_())
