import os
import sys
from src.core.constants import WINDOW_WIDTH, WINDOW_HEIGHT

# Dynamically set PYTHONPATH in .env
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.environ["PYTHONPATH"] = project_root
sys.path.append(project_root)

from PyQt5.QtWidgets import QApplication
from qt.main_window import VTKMainWindow
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
import vtk
from qt.callbacks import toggle_visibility
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from src.core.visualization import configure_window, set_mathematical_view
from src.core.constants import WINDOW_WIDTH, WINDOW_HEIGHT, colors
from src.core import CustomInteractorStyle
from src.utils.surface_utils import (
    create_implicit_surface_actor,
    set_z_gradient_coloring,
)
from src.utils.line_utils import create_axes
from qt.vtk_widget import VTKWidget

x_min, x_max, y_min, y_max, z_min, z_max = -10, 10, -10, 10, -10, 10


class PlotFunc(VTKWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.renderer.SetBackground(colors.GetColor3d("dark_blue"))

        # Add axes
        self.math_axes = create_axes(length=10)
        self.renderer.AddActor(self.math_axes)

        def get_surface_actor(implicit_function, bounds):
            surface_actor = create_implicit_surface_actor(implicit_function, bounds)
            set_z_gradient_coloring(
                surface_actor, colors.GetColor3d("emerald"), colors.GetColor3d("coral")
            )
            return surface_actor

        # Add actors
        def implicit_equation(x, y, z):
            return x**2 + y**2 - z**2 - 1

        surface_actor = get_surface_actor(
            implicit_equation, (x_min, x_max, y_min, y_max, z_min, z_max)
        )
        self.renderer.AddActor(surface_actor)

        # Create a toggle button for axes visibility
        self.toggle_button = QPushButton("Toggle Axes Visibility", self)
        self.toggle_button.clicked.connect(
            lambda: toggle_visibility(self.vtk_widget, self.math_axes)
        )
        self.layout.addWidget(self.toggle_button)

        # Initialize the interactor
        set_mathematical_view(self.renderer)
        self.vtk_widget.GetRenderWindow().Render()
        self.interactor.Initialize()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VTKMainWindow(PlotFunc())
    window.setWindowTitle("Function Plotter")
    window.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
    window.show()
    sys.exit(app.exec_())
