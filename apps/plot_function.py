import os
import sys

# Dynamically set PYTHONPATH in .env
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.environ["PYTHONPATH"] = project_root
sys.path.append(project_root)

from PyQt5.QtWidgets import (
    QApplication,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)
from qt.main_window import VTKMainWindow
from qt.callbacks import toggle_visibility
from src.core.visualization import set_mathematical_view
from src.core.constants import (
    colors,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    X_MIN,
    X_MAX,
    Y_MIN,
    Y_MAX,
    Z_MIN,
    Z_MAX,
    CONTROL_PANEL_WIDTH,
)
from src.utils.surface_utils import (
    create_implicit_surface_actor,
    set_z_gradient_coloring,
)
from src.utils.line_utils import create_axes
from qt.vtk_widget import VTKWidget
from qt.sliders import add_range_sliders


class PlotFunc(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vtk_widget = VTKWidget(self)
        self.renderer = self.vtk_widget.renderer
        self.renderer.SetBackground(colors.GetColor3d("dark_blue"))

        # A horizontal layout for placing the control layout to the left of the rendering window
        self.layout = QHBoxLayout(self)

        # A vertical layout for the control widgets
        control_layout = QVBoxLayout()

        # Initialize bounds
        self.x_min, self.x_max = X_MIN, X_MAX
        self.y_min, self.y_max = Y_MIN, Y_MAX
        self.z_min, self.z_max = Z_MIN, Z_MAX

        # Create sliders
        add_range_sliders(
            self,
            (self.x_min, self.x_max, self.y_min, self.y_max, self.z_min, self.z_max),
            control_layout,
        )

        # Create a toggle button for axes visibility
        self.toggle_button = QPushButton("Toggle Axes Visibility", self)
        self.toggle_button.clicked.connect(
            lambda: toggle_visibility(self.vtk_widget, self.math_axes)
        )
        control_layout.addWidget(self.toggle_button)

        # Set fixed width for the control panel
        control_widget = QWidget()
        control_widget.setLayout(control_layout)
        control_widget.setFixedWidth(CONTROL_PANEL_WIDTH)

        # Add the control and the rendering layout to the main layout
        self.layout.addWidget(control_widget)
        self.layout.addWidget(self.vtk_widget, stretch=1)

        # Add axes
        self.math_axes = create_axes()
        self.renderer.AddActor(self.math_axes)

        # Add function
        self.update_function()

        # Initialize the interactor
        set_mathematical_view(self.renderer)
        self.vtk_widget.GetRenderWindow().Render()
        self.vtk_widget.interactor.Initialize()

    def update_function(self):
        self.x_min, self.x_max = self.x_slider.getRange()
        self.y_min, self.y_max = self.y_slider.getRange()
        self.z_min, self.z_max = self.z_slider.getRange()

        def implicit_equation(x, y, z):
            return x**2 + y**2 - z**2 - 1

        surface_actor = create_implicit_surface_actor(
            implicit_equation,
            (self.x_min, self.x_max, self.y_min, self.y_max, self.z_min, self.z_max),
        )
        set_z_gradient_coloring(
            surface_actor, colors.GetColor3d("emerald"), colors.GetColor3d("coral")
        )

        self.renderer.RemoveAllViewProps()
        self.renderer.AddActor(self.math_axes)
        self.renderer.AddActor(surface_actor)
        self.vtk_widget.GetRenderWindow().Render()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VTKMainWindow(PlotFunc())
    window.setWindowTitle("Function Plotter")
    window.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
    window.show()
    sys.exit(app.exec_())
