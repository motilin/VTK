import os
import sys

# Dynamically set PYTHONPATH in .env
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.environ["PYTHONPATH"] = project_root
sys.path.append(project_root)

from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
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
)
from src.utils.surface_utils import (
    create_implicit_surface_actor,
    set_z_gradient_coloring,
)
from src.utils.line_utils import create_axes
from qt.widgets import VTKWidget, ControlWidget
from src.math.implicit_functions import FUNCS


class PlotFunc(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vtk_widget = VTKWidget(self)
        self.control_widget = ControlWidget(self)
        self.renderer = self.vtk_widget.renderer
        self.renderer.SetBackground(colors.GetColor3d("dark_blue"))
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        # Create an axes actor
        self.math_axes = create_axes()

        # Initialize bounds
        self.x_min, self.x_max = X_MIN, X_MAX
        self.y_min, self.y_max = Y_MIN, Y_MAX
        self.z_min, self.z_max = Z_MIN, Z_MAX

        # Initialize coefficients
        self.coeff_a = 1
        self.coeff_b = 1
        self.coeff_c = 1
        self.implicit_function = FUNCS["Custom"](
            self.coeff_a, self.coeff_b, self.coeff_c
        )

        # Populate the control widget
        self.control_widget.add_range_sliders(
            (self.x_min, self.x_max, self.y_min, self.y_max, self.z_min, self.z_max),
            self.update_function,
        )
        self.control_widget.add_dropdown(
            "Implicit Function",
            FUNCS.keys(),
            lambda idx: (
                setattr(
                    self,
                    "implicit_function",
                    FUNCS[list(FUNCS.keys())[idx]](
                        self.coeff_a, self.coeff_b, self.coeff_c
                    )
                ),
                self.update_function()
            ),
        )
        self.control_widget.add_button(
            "Toggle Axes Visibility",
            lambda: toggle_visibility(self.vtk_widget, self.math_axes),
        )

        # Add the control and the rendering widgets to the main layout
        self.layout.addWidget(self.control_widget)
        self.layout.addWidget(self.vtk_widget, stretch=1)

        # Update the function, initialize the renderer, and render the scene
        self.update_function()
        set_mathematical_view(self.renderer)
        self.vtk_widget.get_render_window().Render()
        self.vtk_widget.interactor.Initialize()

    def update_function(self):
        self.x_min, self.x_max = self.control_widget.x_slider.getRange()
        self.y_min, self.y_max = self.control_widget.y_slider.getRange()
        self.z_min, self.z_max = self.control_widget.z_slider.getRange()

        surface_actor = create_implicit_surface_actor(
            self.implicit_function,
            (self.x_min, self.x_max, self.y_min, self.y_max, self.z_min, self.z_max),
        )
        set_z_gradient_coloring(
            surface_actor, colors.GetColor3d("emerald"), colors.GetColor3d("coral")
        )

        self.renderer.RemoveAllViewProps()
        self.renderer.AddActor(self.math_axes)
        self.renderer.AddActor(surface_actor)
        self.vtk_widget.get_render_window().Render()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VTKMainWindow(PlotFunc())
    window.setWindowTitle("Function Plotter")
    window.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
    window.show()
    sys.exit(app.exec_())
