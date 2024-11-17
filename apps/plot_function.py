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
from src.core.interactor import set_mathematical_view
from src.core.constants import (
    COLORS,
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
    create_func_surface_actor,
    set_z_gradient_coloring,
)
from src.utils.line_utils import create_axes, create_func_traces_actor
from qt.widgets import VTKWidget, ControlWidget
from src.math.implicit_functions import FUNCS
from src.math.func_utils import parse_function
from src.utils.cube_axes import create_cube_axes_actor


class PlotFunc(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vtk_widget = VTKWidget(self)
        self.control_widget = ControlWidget(self)
        self.renderer = self.vtk_widget.renderer
        self.renderer.SetBackground(COLORS.GetColor3d("dark_blue"))
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        # Initialize bounds
        self.x_min, self.x_max = X_MIN, X_MAX
        self.y_min, self.y_max = Y_MIN, Y_MAX
        self.z_min, self.z_max = Z_MIN, Z_MAX
        
        # Create an axes actor
        self.math_axes = create_axes()
        self.cube_axes = create_cube_axes_actor(
            (self.x_min, self.x_max, self.y_min, self.y_max, self.z_min, self.z_max), self.renderer
        )
        self.cube_axes.SetVisibility(False)

        # Initialize coefficients
        self.coeff_a = 1
        self.coeff_b = 1
        self.coeff_c = 1

        # Initialize function name and visibitliy
        self.custom_func = None
        self.func_name = list(FUNCS.keys())[0]
        self.show_traces = True
        self.show_surface = False
        self.trace_spacing = 1

        # Populate the control widget
        self.control_widget.add_range_sliders(
            (self.x_min, self.x_max, self.y_min, self.y_max, self.z_min, self.z_max),
            self.update_function,
        )
        self.control_widget.add_slider(
            (-3, 3),
            1,
            "a",
            lambda val: (
                setattr(self, "coeff_a", val),
                self.update_function(),
            ),
        )
        self.control_widget.add_slider(
            (-3, 3),
            1,
            "b",
            lambda val: (
                setattr(self, "coeff_b", val),
                self.update_function(),
            ),
        )
        self.control_widget.add_slider(
            (-3, 3),
            1,
            "c",
            lambda val: (
                setattr(self, "coeff_c", val),
                self.update_function(),
            ),
        )
        self.control_widget.add_dropdown(
            "Implicit Function",
            FUNCS.keys(),
            lambda idx: (
                setattr(
                    self,
                    "func_name",
                    list(FUNCS.keys())[idx],
                ),
                self.update_function(),
            ),
        )
        self.control_widget.add_slider(
            (0.1, 3),
            1,
            "Trace Spacing",
            lambda val: (
                setattr(self, "trace_spacing", val),
                self.update_function(),
            ),
        )
        self.control_widget.add_checkbox(
            "Surface",
            False,
            lambda state: (
                setattr(self, "show_surface", state),
                self.update_function(),
            ),
        )
        self.control_widget.add_checkbox(
            "Traces",
            True,
            lambda state: (
                setattr(self, "show_traces", state),
                self.update_function(),
            ),
        )
        self.control_widget.add_checkbox(
            "Axes",
            True,
            lambda state: (
                self.math_axes.SetVisibility(state),
                self.vtk_widget.get_render_window().Render(),
            ),
        )
        self.control_widget.add_checkbox(
            "Cube Axes",
            False,
            lambda state: (
                self.cube_axes.SetVisibility(state),
                self.vtk_widget.get_render_window().Render(),
            ),
        )
        # parse the custom function string as a python code and set it to self.custom_func
        self.control_widget.add_textbox(
            "Custom Function:",
            lambda text: (
                setattr(self, "custom_func", text),
                self.update_function(),
            ),
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
        self.renderer.RemoveAllViewProps()
        self.renderer.AddActor(self.math_axes)
        
        self.cube_axes.SetBounds(self.x_min, self.x_max, self.y_min, self.y_max, self.z_min, self.z_max)
        self.renderer.AddActor(self.cube_axes)

        func = FUNCS[self.func_name]
        if self.func_name == "Custom" and self.custom_func:
            try:
                parsed = parse_function(self.custom_func)
                func = parsed if parsed else func
            except Exception as e:
                pass

        if self.show_surface:
            surface_actor = create_func_surface_actor(
                func(self.coeff_a, self.coeff_b, self.coeff_c),
                (
                    self.x_min,
                    self.x_max,
                    self.y_min,
                    self.y_max,
                    self.z_min,
                    self.z_max,
                ),
            )
            set_z_gradient_coloring(
                surface_actor, COLORS.GetColor3d("emerald"), COLORS.GetColor3d("coral")
            )
            self.renderer.AddActor(surface_actor)
        if self.show_traces:
            traces_actor = create_func_traces_actor(
                func(self.coeff_a, self.coeff_b, self.coeff_c),
                (
                    self.x_min,
                    self.x_max,
                    self.y_min,
                    self.y_max,
                    self.z_min,
                    self.z_max,
                ),
                self.trace_spacing,
            )
            self.renderer.AddActor(traces_actor)

        self.vtk_widget.get_render_window().Render()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VTKMainWindow(PlotFunc())
    window.setWindowTitle("Function Plotter")
    window.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
    window.show()
    sys.exit(app.exec_())
