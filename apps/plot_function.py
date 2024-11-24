import os, sys
import sympy as sp

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
    DEFAULT_SLIDER_BOUNDS,
)
from src.utils.line_utils import create_axes
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

        # Set up depth peeling (for transparency)
        self.renderer.SetUseDepthPeeling(1)
        self.renderer.SetOcclusionRatio(0.1)
        self.renderer.SetMaximumNumberOfPeels(4)
        self.vtk_widget.get_render_window().SetMultiSamples(0)
        self.vtk_widget.get_render_window().SetAlphaBitPlanes(1)

        self.functions = []
        self.func_names = []
        self.coeffs = dict()
        self.coeffs_bounds = dict()
        self.active_func = None

        # Initialize global bounds
        self.global_x_min, self.global_x_max = X_MIN, X_MAX
        self.global_y_min, self.global_y_max = Y_MIN, Y_MAX
        self.global_z_min, self.global_z_max = Z_MIN, Z_MAX

        # Create axes actor
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

        self.x_label, self.x_min, self.x_max = self.control_widget.add_range_text_boxes(
            "X range", (self.global_x_min, self.global_x_max), self.update_x_range
        )

        self.y_label, self.y_min, self.y_max = self.control_widget.add_range_text_boxes(
            "Y range", (self.global_y_min, self.global_y_max), self.update_y_range
        )

        self.z_label, self.z_min, self.z_max = self.control_widget.add_range_text_boxes(
            "Z range", (self.global_z_min, self.global_z_max), self.update_z_range
        )

        self.t_range_slider = self.control_widget.add_range_slider(
            DEFAULT_SLIDER_BOUNDS,
            (0, 1),
            "t",
            self.update_t_range,
        )
        self.t_range_slider.setVisible(False)

        self.u_range_slider = self.control_widget.add_range_slider(
            DEFAULT_SLIDER_BOUNDS,
            (0, 1),
            "u",
            self.update_u_range,
        )
        self.u_range_slider.setVisible(False)

        self.v_range_slider = self.control_widget.add_range_slider(
            DEFAULT_SLIDER_BOUNDS,
            (0, 1),
            "v",
            self.update_v_range,
        )
        self.v_range_slider.setVisible(False)

        self.surface_colors = self.control_widget.add_color_picker(
            "Surface colors",
            (DEFAULT_COLOR_START, DEFAULT_COLOR_END),
            (self.update_color_start, self.update_color_end),
            dual=True,
        )

        self.line_color = self.control_widget.add_color_picker(
            "Line color",
            DEFAULT_LINE_COLOR,
            self.update_line_color,
        )

        self.trace_spacing_slider = self.control_widget.add_slider(
            DEFAULT_SLIDER_BOUNDS, 1, "Trace Spacing", self.update_trace_spacing
        )

        self.line_thickness = self.control_widget.add_slider(
            DEFAULT_SLIDER_BOUNDS,
            2,
            "Line Thickness",
            self.update_line_thickness,
        )

        self.opacity = self.control_widget.add_slider(
            (0, 1),
            1,
            "Opacity",
            self.update_opacity,
        )

        self.dash_spacing = self.control_widget.add_slider(
            DEFAULT_SLIDER_BOUNDS,
            0,
            "Dash Spacing",
            self.update_dash_spacing,
        )

        self.show_surface_checkbox = self.control_widget.add_checkbox(
            "Surface",
            False,
            self.set_show_surface,
        )

        self.show_lines_checkbox = self.control_widget.add_checkbox(
            "Lines",
            True,
            self.set_show_lines,
        )

        self.func_dropdown = self.control_widget.add_dropdown(
            "Active function", self.func_names, self.update_active_func
        )

        self.func_input_textbox = self.control_widget.add_textbox(
            "Functions input:", self.handle_function_input
        )

        self.control_widget.add_label("Global settings:")

        self.global_x_label_text, self.global_x_min_text, self.global_x_max_text = (
            self.control_widget.add_range_text_boxes(
                "X range",
                (self.global_x_min, self.global_x_max),
                lambda val: (
                    setattr(self, "global_x_min", val[0]),
                    setattr(self, "global_x_max", val[1]),
                    self.update_global_bounds(),
                ),
            )
        )
        self.global_y_label_text, self.global_y_min_text, self.global_y_max_text = (
            self.control_widget.add_range_text_boxes(
                "Y range",
                (self.global_y_min, self.global_y_max),
                lambda val: (
                    setattr(self, "global_y_min", val[0]),
                    setattr(self, "global_y_max", val[1]),
                    self.update_global_bounds(),
                ),
            )
        )
        self.global_z_label_text, self.global_z_min_text, self.global_z_max_text = (
            self.control_widget.add_range_text_boxes(
                "Z range",
                (self.global_z_min, self.global_z_max),
                lambda val: (
                    setattr(self, "global_z_min", val[0]),
                    setattr(self, "global_z_max", val[1]),
                    self.update_global_bounds(),
                ),
            )
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

    def update_x_range(self, val):
        if self.active_func:
            self.active_func.x_min = val[0]
            self.active_func.x_max = val[1]
            self.active_func.update_render(self)

    def update_y_range(self, val):
        if self.active_func:
            self.active_func.y_min = val[0]
            self.active_func.y_max = val[1]
            self.active_func.update_render(self)

    def update_z_range(self, val):
        if self.active_func:
            self.active_func.z_min = val[0]
            self.active_func.z_max = val[1]
            self.active_func.update_render(self)

    def update_t_range(self, values, bounds):
        if self.active_func:
            self.active_func.t_range = values
            self.active_func.t_range_bounds = bounds
            self.active_func.update_render(self)

    def update_u_range(self, values, bounds):
        if self.active_func:
            self.active_func.u_range = values
            self.active_func.u_range_bounds = bounds
            self.active_func.update_render(self)

    def update_v_range(self, values, bounds):
        if self.active_func:
            self.active_func.v_range = values
            self.active_func.v_range_bounds = bounds
            self.active_func.update_render(self)

    def update_color_start(self, color):
        if self.active_func:
            self.active_func.color_start = color
            self.active_func.update_render(self)

    def update_color_end(self, color):
        if self.active_func:
            self.active_func.color_end = color
            self.active_func.update_render(self)

    def update_line_color(self, color):
        if self.active_func:
            self.active_func.line_color = color
            self.active_func.update_render(self)

    def update_trace_spacing(self, val, bounds):
        if self.active_func:
            self.active_func.trace_spacing = val
            self.active_func.trace_spacing_bounds = bounds
            self.active_func.update_render(self)

    def update_line_thickness(self, val, bounds):
        if self.active_func:
            self.active_func.thickness = val
            self.active_func.thickness_bounds = bounds
            self.active_func.update_render(self)

    def update_opacity(self, val, bounds):
        if self.active_func:
            self.active_func.opacity = val
            self.active_func.update_render(self)

    def update_dash_spacing(self, val, bounds):
        if self.active_func:
            self.active_func.dash_spacing = val
            self.active_func.dash_spacing_bounds = bounds
            self.active_func.update_render(self)

    def set_show_surface(self, state):
        if self.active_func:
            self.active_func.show_surface = state
            self.active_func.update_render(self)
            if self.active_func.surface_actor:
                self.active_func.surface_actor.SetVisibility(state)
            self.vtk_widget.get_render_window().Render()

    def set_show_lines(self, state):
        if self.active_func:
            self.active_func.show_lines = state
            self.active_func.update_render(self)
            if self.active_func.lines_actor:
                self.active_func.lines_actor.SetVisibility(state)
            self.vtk_widget.get_render_window().Render()

    def update_active_func(self, idx):
        if idx != -1 and len(self.functions) > idx:
            self.active_func = self.functions[idx]
            self.x_min.setText(str(self.active_func.x_min))
            self.x_max.setText(str(self.active_func.x_max))
            self.y_min.setText(str(self.active_func.y_min))
            self.y_max.setText(str(self.active_func.y_max))
            self.z_min.setText(str(self.active_func.z_min))
            self.z_max.setText(str(self.active_func.z_max))
            self.t_range_slider.update_slider(
                self.active_func.t_range_bounds,
                self.active_func.t_range,
            )
            self.u_range_slider.update_slider(
                self.active_func.u_range_bounds,
                self.active_func.u_range,
            )
            self.v_range_slider.update_slider(
                self.active_func.v_range_bounds,
                self.active_func.v_range,
            )
            self.trace_spacing_slider.set_value(
                self.active_func.trace_spacing,
                self.active_func.trace_spacing_bounds,
            )
            self.surface_colors.set_colors(
                (self.active_func.color_start, self.active_func.color_end),
            )
            self.line_color.set_colors(self.active_func.line_color)
            self.line_thickness.set_value(
                self.active_func.thickness, self.active_func.thickness_bounds
            )
            self.opacity.set_value(self.active_func.opacity, (0, 1))
            self.dash_spacing.set_value(
                self.active_func.dash_spacing, self.active_func.dash_spacing_bounds
            )
            self.dash_spacing.set_value(
                self.active_func.dash_spacing, self.active_func.dash_spacing_bounds
            )
            self.show_surface_checkbox.setChecked(self.active_func.show_surface)
            self.show_lines_checkbox.setChecked(self.active_func.show_lines)
            if self.active_func.type == "implicit" or self.active_func.type == "point":
                self.x_label.setVisible(True)
                self.x_min.setVisible(True)
                self.x_max.setVisible(True)
                self.y_label.setVisible(True)
                self.y_min.setVisible(True)
                self.y_max.setVisible(True)
                self.z_label.setVisible(True)
                self.z_min.setVisible(True)
                self.z_max.setVisible(True)
                self.t_range_slider.setVisible(False)
                self.u_range_slider.setVisible(False)
                self.v_range_slider.setVisible(False)
                self.trace_spacing_slider.setVisible(True)
                self.dash_spacing.setVisible(False)
            elif self.active_func.type == "parametric-1":
                self.x_label.setVisible(False)
                self.x_min.setVisible(False)
                self.x_max.setVisible(False)
                self.y_label.setVisible(False)
                self.y_min.setVisible(False)
                self.y_max.setVisible(False)
                self.z_label.setVisible(False)
                self.z_min.setVisible(False)
                self.z_max.setVisible(False)
                self.t_range_slider.setVisible(True)
                self.u_range_slider.setVisible(False)
                self.v_range_slider.setVisible(False)
                self.trace_spacing_slider.setVisible(False)
                self.dash_spacing.setVisible(True)
            elif self.active_func.type == "parametric-2":
                self.x_label.setVisible(False)
                self.x_min.setVisible(False)
                self.x_max.setVisible(False)
                self.y_label.setVisible(False)
                self.y_min.setVisible(False)
                self.y_max.setVisible(False)
                self.z_label.setVisible(False)
                self.z_min.setVisible(False)
                self.z_max.setVisible(False)
                self.t_range_slider.setVisible(False)
                self.u_range_slider.setVisible(True)
                self.v_range_slider.setVisible(True)
                self.trace_spacing_slider.setVisible(True)
                self.dash_spacing.setVisible(False)

    def update_slider(self, coeff):
        return lambda val, bounds: (
            self.coeffs.update({coeff: val}),
            self.coeffs_bounds.update({coeff: bounds}),
            self.update_functions(coeff),
        )

    def update_coeff_sliders(self):
        new_coeff_dict = dict()
        missing_sliders = set()
        for func in self.functions:
            for coeff in func.coeffs:
                if coeff in self.coeffs:
                    new_coeff_dict[coeff] = self.coeffs[coeff]
                else:
                    new_coeff_dict[coeff] = 1
                    missing_sliders.add(coeff)
        for coeff in self.coeffs:
            if coeff not in new_coeff_dict:
                self.control_widget.remove_slider_by_label(coeff.name)
        self.coeffs = new_coeff_dict
        for coeff in list(missing_sliders):
            self.control_widget.add_slider(
                DEFAULT_SLIDER_BOUNDS,
                1,
                coeff.name,
                self.update_slider(coeff),
            )

    def handle_function_input(self, text):
        self.func_names = []
        self.active_func = None
        new_functions = []

        # Parse the input text and create a Func object for each function
        for func_text in text.split("\n"):
            func = Func(func_text.strip())
            if func.legal and func not in new_functions:
                self.func_names.append(func.str)
                if func in self.functions:
                    new_functions.append(self.functions[self.functions.index(func)])
                else:
                    new_functions.append(func)

        # Remove actors for functions that are no longer present
        for func in self.functions:
            if func not in new_functions:
                if func.surface_actor:
                    self.renderer.RemoveActor(func.surface_actor)
                if func.lines_actor:
                    self.renderer.RemoveActor(func.lines_actor)
        self.vtk_widget.get_render_window().Render()

        # Update the functions list and coefficient sliders
        self.functions = new_functions
        self.update_coeff_sliders()

        # Update the dropdown with the new function names
        self.control_widget.update_dropdown(self.func_dropdown, self.func_names)

        # Update the render for each function
        for func in self.functions:
            func.update_render(self)

    def marshalize(self):
        return {
            "functions": [func.marshalize() for func in self.functions],
            "background_color": list(self.renderer.GetBackground()),
            "global_bounds": {
                "x_min": self.global_x_min,
                "x_max": self.global_x_max,
                "y_min": self.global_y_min,
                "y_max": self.global_y_max,
                "z_min": self.global_z_min,
                "z_max": self.global_z_max,
            },
            "coeffs": {str(coeff): self.coeffs[coeff] for coeff in self.coeffs},
            "coeffs_bounds": {
                str(coeff): self.coeffs_bounds[coeff] for coeff in self.coeffs
            },
            "camera": self.renderer.GetActiveCamera().GetViewUp(),
        }

    def unmarshalize(self, data):
        self.renderer.SetBackground(data["background_color"])
        self.global_x_min = data["global_bounds"]["x_min"]
        self.global_x_max = data["global_bounds"]["x_max"]
        self.global_y_min = data["global_bounds"]["y_min"]
        self.global_y_max = data["global_bounds"]["y_max"]
        self.global_z_min = data["global_bounds"]["z_min"]
        self.global_z_max = data["global_bounds"]["z_max"]
        # self.x_min.setText(str(self.global_x_min))
        self.global_x_min_text.setText(str(self.global_x_min))
        self.global_x_max_text.setText(str(self.global_x_max))
        self.global_y_min_text.setText(str(self.global_y_min))
        self.global_y_max_text.setText(str(self.global_y_max))
        self.global_z_min_text.setText(str(self.global_z_min))
        self.global_z_max_text.setText(str(self.global_z_max))
        self.update_global_bounds()
        self.functions = []
        for func_data in data["functions"]:
            func = Func("")
            func.unmarshalize(func_data)
            self.functions.append(func)
            self.func_names.append(func.str)
        self.func_input_textbox.setText("\n".join(self.func_names))
        self.update_coeff_sliders()
        self.control_widget.update_dropdown(self.func_dropdown, self.func_names)
        self.update_active_func(0)
        for func in self.functions:
            func.update_render(self)
        for coeff in data["coeffs"]:
            coeff_symbol = sp.Symbol(coeff)
            self.coeffs[coeff_symbol] = data["coeffs"][coeff]
            self.coeffs_bounds[coeff_symbol] = data["coeffs_bounds"][coeff]
            self.control_widget.update_slider_by_label(
                coeff, self.coeffs[coeff_symbol], self.coeffs_bounds[coeff_symbol]
            )
        self.renderer.GetActiveCamera().SetViewUp(data["camera"])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VTKMainWindow(PlotFunc())
    sys.exit(app.exec_())
