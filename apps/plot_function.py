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
    X_MIN,
    X_MAX,
    Y_MIN,
    Y_MAX,
    Z_MIN,
    Z_MAX,
    DEFAULT_BACKGROUND_COLOR,
    DEFAULT_COLOR_START,
    DEFAULT_COLOR_END,
    DEFAULT_LINE_COLOR,
    SCALE_FACTOR,
)
from src.utils.surface_utils import (
    create_func_surface_actor,
    set_z_gradient_coloring,
)
from src.utils.line_utils import create_axes, create_func_traces_actor
from qt.widgets import VTKWidget, ControlWidget
from src.math.implicit_functions import FUNCS
from src.math.func_utils import Func
from src.utils.cube_axes import create_cube_axes_actor


class PlotFunc(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vtk_widget = VTKWidget(self)
        self.control_widget = ControlWidget(self)
        self.renderer = self.vtk_widget.renderer
        self.renderer.SetBackground(DEFAULT_BACKGROUND_COLOR)
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.control_widget)
        self.layout.addWidget(self.vtk_widget, stretch=1)

        self.functions = []
        self.func_names = []
        self.coeffs = dict()
        self.active_func = None

        # Initialize bounds
        self.global_x_min, self.global_x_max = X_MIN, X_MAX
        self.global_y_min, self.global_y_max = Y_MIN, Y_MAX
        self.global_z_min, self.global_z_max = Z_MIN, Z_MAX

        # Create an axes actor
        self.math_axes = create_axes()
        self.cube_axes = create_cube_axes_actor(
            (
                self.global_x_min,
                self.global_x_max,
                self.global_y_min,
                self.global_y_max,
                self.global_z_min,
                self.global_z_max,
            ),
            self.renderer,
        )
        self.cube_axes.SetVisibility(False)

        # Initialize function name and visibitliy
        self.custom_func = None
        self.show_traces = True
        self.show_surface = False
        self.trace_spacing = 1

        # Populate the control widget
        def update_x_range(val):
            if self.active_func:
                self.active_func.x_min = val[0]
                self.active_func.x_max = val[1]
                self.active_func.update_render(self)

        x_min, x_max = self.control_widget.add_range_text_boxes(
            "X range", (self.global_x_min, self.global_x_max), update_x_range
        )

        def update_y_range(val):
            if self.active_func:
                self.active_func.y_min = val[0]
                self.active_func.y_max = val[1]
                self.active_func.update_render(self)

        y_min, y_max = self.control_widget.add_range_text_boxes(
            "Y range", (self.global_y_min, self.global_y_max), update_y_range
        )

        def update_z_range(val):
            if self.active_func:
                self.active_func.z_min = val[0]
                self.active_func.z_max = val[1]
                self.active_func.update_render(self)

        z_min, z_max = self.control_widget.add_range_text_boxes(
            "Z range", (self.global_z_min, self.global_z_max), update_z_range
        )

        def update_trace_spacing(val):
            if self.active_func:
                self.active_func.trace_spacing = val
                self.active_func.update_render(self)

        trace_spacing_slider = self.control_widget.add_slider(
            (0.1, 3), 1, "Trace Spacing", update_trace_spacing
        )

        def update_color_start(color):
            if self.active_func:
                self.active_func.color_start = color
                self.active_func.update_render(self)

        def update_color_end(color):
            if self.active_func:
                self.active_func.color_end = color
                self.active_func.update_render(self)

        surface_colors = self.control_widget.add_color_picker(
            "Surface colors",
            (DEFAULT_COLOR_START, DEFAULT_COLOR_END),
            (update_color_start, update_color_end),
            dual=True,
        )

        def update_line_color(color):
            if self.active_func:
                self.active_func.line_color = color
                self.active_func.update_render(self)

        line_color = self.control_widget.add_color_picker(
            "Line color",
            DEFAULT_LINE_COLOR,
            update_line_color,
        )

        def set_show_surface(state):
            if self.active_func:
                self.active_func.show_surface = state
                if self.active_func.surface_actor:
                    self.active_func.surface_actor.SetVisibility(state)
                else:
                    self.active_func.update_render(self)
                self.vtk_widget.get_render_window().Render()

        show_surface_checkbox = self.control_widget.add_checkbox(
            "Surface",
            False,
            set_show_surface,
        )

        def set_show_traces(state):
            if self.active_func:
                self.active_func.show_traces = state
                if self.active_func.traces_actor:
                    self.active_func.traces_actor.SetVisibility(state)
                else:
                    self.active_func.update_render(self)
                self.vtk_widget.get_render_window().Render()

        show_traces_checkbox = self.control_widget.add_checkbox(
            "Traces",
            True,
            set_show_traces,
        )

        def update_active_func(idx):
            if idx != -1 and len(self.functions) > idx:
                self.active_func = self.functions[idx]
                x_min.setText(str(self.active_func.x_min))
                x_max.setText(str(self.active_func.x_max))
                y_min.setText(str(self.active_func.y_min))
                y_max.setText(str(self.active_func.y_max))
                z_min.setText(str(self.active_func.z_min))
                z_max.setText(str(self.active_func.z_max))
                trace_spacing_slider.setValue(
                    int(self.active_func.trace_spacing) * SCALE_FACTOR
                )
                surface_colors.set_colors(
                    (self.active_func.color_start, self.active_func.color_end),
                )
                line_color.set_colors(self.active_func.line_color)
                show_surface_checkbox.setChecked(self.active_func.show_surface)
                show_traces_checkbox.setChecked(self.active_func.show_traces)

        func_dropdown = self.control_widget.add_dropdown(
            "Active function", self.func_names, update_active_func
        )

        def update_coeff_sliders(self):
            new_coeff_dict = dict()
            for func in self.functions:
                for coeff in func.coeffs:
                    if coeff in self.coeffs:
                        new_coeff_dict[coeff] = self.coeffs[coeff]
                    elif coeff not in new_coeff_dict:
                        new_coeff_dict[coeff] = 1
                        self.control_widget.add_slider(
                            (0.1, 3),
                            1,
                            coeff.name,
                            lambda val, coeff=coeff: (
                                self.coeffs.update({coeff: val}),
                                self.update_functions(coeff),
                            ),
                        )
            for coeff in self.coeffs:
                if coeff not in new_coeff_dict:
                    self.control_widget.remove_layout_by_label(coeff.name)
            self.coeffs = new_coeff_dict

        def handle_function_input(text):
            self.func_names = []
            self.active_func = None
            new_functions = []

            # Parse the input text and create a Func object for each function
            for func_text in text.split("\n"):
                func = Func(func_text.strip())
                if func.legal and func not in new_functions:
                    self.func_names.append(func.latex)
                    if func in self.functions:
                        new_functions.append(self.functions[self.functions.index(func)])
                    else:
                        new_functions.append(func)

            # Remove actors for functions that are no longer present
            for func in self.functions:
                if func not in new_functions:
                    if func.surface_actor:
                        self.renderer.RemoveActor(func.surface_actor)
                    if func.traces_actor:
                        self.renderer.RemoveActor(func.traces_actor)
            self.vtk_widget.get_render_window().Render()

            # Update the functions list and coefficient sliders
            self.functions = new_functions
            update_coeff_sliders(self)

            # Update the dropdown with the new function names
            self.control_widget.update_dropdown(func_dropdown, self.func_names)

            # Update the render for each function
            for func in self.functions:
                func.update_render(self)

        self.control_widget.add_textbox("Functions input:", handle_function_input)

        self.control_widget.add_label("Global settings:")

        self.control_widget.add_range_text_boxes(
            "X range",
            (self.global_x_min, self.global_x_max),
            lambda val: (
                setattr(self, "global_x_min", val[0]),
                setattr(self, "global_x_max", val[1]),
                self.update_global_bounds(),
            ),
        )
        self.control_widget.add_range_text_boxes(
            "Y range",
            (self.global_y_min, self.global_y_max),
            lambda val: (
                setattr(self, "global_y_min", val[0]),
                setattr(self, "global_y_max", val[1]),
                self.update_global_bounds(),
            ),
        )
        self.control_widget.add_range_text_boxes(
            "Z range",
            (self.global_z_min, self.global_z_max),
            lambda val: (
                setattr(self, "global_z_min", val[0]),
                setattr(self, "global_z_max", val[1]),
                self.update_global_bounds(),
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
        self.control_widget.add_color_picker(
            "Background Color",
            DEFAULT_BACKGROUND_COLOR,
            lambda color: (
                self.renderer.SetBackground(color),
                self.vtk_widget.get_render_window().Render(),
            ),
        )

        # Update the function, initialize the renderer, and render the scene
        self.update_global_bounds()
        set_mathematical_view(self.renderer)
        self.vtk_widget.get_render_window().Render()
        self.vtk_widget.interactor.Initialize()

    def update_functions(self, coeff):
        for func in self.functions:
            if coeff in func.coeffs:
                func.update_render(self)

    def update_global_bounds(self):
        self.renderer.RemoveAllViewProps()
        self.renderer.AddActor(self.math_axes)

        self.cube_axes.SetBounds(
            self.global_x_min,
            self.global_x_max,
            self.global_y_min,
            self.global_y_max,
            self.global_z_min,
            self.global_z_max,
        )
        self.renderer.AddActor(self.cube_axes)
        
        for func in self.functions:
            func.update_render(self)

        self.vtk_widget.get_render_window().Render()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VTKMainWindow(PlotFunc())
    sys.exit(app.exec_())
