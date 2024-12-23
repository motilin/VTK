import re, copy, vtk
from rich.console import Console
from rich.markdown import Markdown
import numpy as np
from src.core.constants import (
    X_MIN,
    X_MAX,
    Y_MIN,
    Y_MAX,
    Z_MIN,
    Z_MAX,
    COLORS,
    DEFAULT_COLOR_START,
    DEFAULT_COLOR_END,
    DEFAULT_LINE_COLOR,
    DEFAULT_SLIDER_BOUNDS,
)
from src.utils.surface_utils import (
    create_func_surface_actor,
    set_z_gradient_coloring,
    create_parametric_func_surface_actor,
    create_point_actor,
)
from src.utils.line_utils import (
    create_func_traces_actor,
    create_parametric_curve_actor,
    create_parametric_surface_traces_actor,
    create_horizontal_contours_actor,
    create_parametric_horizontal_contours_actor,
)
import sympy as sp
from sympy.matrices import MatrixBase, ImmutableDenseMatrix

from src.math.text_preprocessing import parse


class Func:
    def __init__(self, text):
        self.text = text
        self.x_min, self.x_max = X_MIN, X_MAX
        self.y_min, self.y_max = Y_MIN, Y_MAX
        self.z_min, self.z_max = Z_MIN, Z_MAX
        self.t_range = (0, 1)
        self.u_range = (0, 1)
        self.v_range = (0, 1)
        self.t_range_bounds = (-DEFAULT_SLIDER_BOUNDS[1], DEFAULT_SLIDER_BOUNDS[1])
        self.u_range_bounds = (-DEFAULT_SLIDER_BOUNDS[1], DEFAULT_SLIDER_BOUNDS[1])
        self.v_range_bounds = (-DEFAULT_SLIDER_BOUNDS[1], DEFAULT_SLIDER_BOUNDS[1])
        self.trace_spacing = 1
        self.trace_spacing_bounds = DEFAULT_SLIDER_BOUNDS
        self.thickness = 1
        self.thickness_bounds = DEFAULT_SLIDER_BOUNDS
        self.dash_spacing = 0
        self.dash_spacing_bounds = DEFAULT_SLIDER_BOUNDS
        self.opacity = 1.0
        self.color_start = DEFAULT_COLOR_START
        self.color_end = DEFAULT_COLOR_END
        self.line_color = DEFAULT_LINE_COLOR
        self.legal = False
        self.type = None
        self.show_surface = True
        self.show_lines = True
        self.show_contour = False
        self.func = sp.Basic()
        self.coeffs = set()
        self.surface_actor = None
        self.lines_actor = None
        self.contour_actor = None
        self.console = Console()
        self.parse_function()

    def parse_function(self):
        try:
            if self.text.strip() == "":
                self.console.print(":arrow_forward:")
                self.legal = False
                return
            expr = parse(self.text)
            if not expr:
                self.legal = False
                return
            if isinstance(expr, sp.Equality):
                expr = sp.simplify(expr.lhs) - sp.simplify(expr.rhs)
            self.func = expr

            if isinstance(expr, MatrixBase):
                if expr.shape == (3, 1):
                    u, v, t = sp.symbols("u v t")
                    all_symbols = expr.free_symbols
                    if (
                        t in all_symbols
                        and u not in all_symbols
                        and v not in all_symbols
                    ):
                        self.coeffs = all_symbols - {t}
                        self.type = "parametric-1"
                        self.legal = True
                        # self.reparametrize()
                    elif u in all_symbols and v in all_symbols and t not in all_symbols:
                        self.coeffs = all_symbols - {u, v}
                        self.type = "parametric-2"
                        self.legal = True
                    elif (
                        t not in all_symbols
                        and u not in all_symbols
                        and v not in all_symbols
                    ):
                        self.coeffs = all_symbols
                        self.type = "point"
                        self.legal = True

            elif isinstance(expr, sp.Basic):
                x, y, z = sp.symbols("x y z")
                self.coeffs = expr.free_symbols - {x, y, z}
                diff = len(expr.free_symbols) - len(self.coeffs)
                if diff == 0:
                    self.type = "number"
                    self.legal = False
                    self.console.print(f"{self.text} = {expr.evalf()}")  # type: ignore
                elif diff == 1:
                    self.type = "single"
                    self.legal = False
                    self.console.print(f"{self.text} = {expr}")
                else:
                    self.type = "implicit"
                    self.legal = True

            else:
                self.legal = False

            if self.legal:
                # self.str = sp.latex(self.func)
                self.str = self.text

        except Exception as e:
            print(e)
            self.legal = False

    def reparametrize(self):
        try:
            # parametrize the curve with respect to arc length
            speed = sp.diff(self.func, sp.symbols("t")).norm()  # type: ignore
            t, s = sp.symbols("t s")
            arc_length_func = sp.integrate(speed, (t, 0, t))
            t_arc_length = sp.simplify(sp.solve(arc_length_func - s, t)[0])
            reparametrized = self.func.subs(t, t_arc_length)
            reparametrized = sp.pretty(reparametrized)
            self.console.print(f"{self.text} reparametrized:\n{reparametrized}")
        except Exception as e:
            print("Error reparametrizing: ", e)

    def update_render(self, widget):
        if not self.legal:
            return
        func = copy.copy(self.func)
        global_bounds = self.get_bounds(widget)

        # Replace coefficients with values
        for coeff in self.coeffs:
            if coeff in widget.coeffs:
                # if isinstance(func, sp.Basic):
                func = func.subs(coeff, widget.coeffs[coeff])
                # elif isinstance(func, tuple):
                # func = tuple([f.subs(coeff, widget.coeffs[coeff]) for f in func])
            else:
                raise ValueError(f"Missing coefficient: {coeff}")

        if sp.S.ComplexInfinity in sp.preorder_traversal(func):
            return

        # Create a numpy function from the sympy function
        if isinstance(func, sp.Basic) and self.type == "implicit":
            x, y, z = sp.symbols("x y z")
            np_func = sp.lambdify((x, y, z), func, "numpy")
        elif isinstance(func, MatrixBase):
            func = tuple([item for sublist in func.tolist() for item in sublist])
            if self.type == "parametric-1":
                t = sp.symbols("t")
                np_func = sp.lambdify(t, func, "numpy")
            elif self.type == "parametric-2":
                u, v = sp.symbols("u v")
                np_func = sp.lambdify((u, v), func, "numpy")
            elif self.type == "point":
                np_func = func

        def safe_np_func(*args):
            try:
                # Check for complex or non-real results
                def sanitize_result(r):
                    if isinstance(r, np.ndarray):
                        return r
                    # Completely filter out complex numbers or non-real results
                    if not np.isreal(r):
                        return np.nan  # or np.inf, depending on your specific needs

                    # Optional: Add additional domain validation if needed
                    # For example, checking for valid ranges or infinite values
                    if np.isinf(r) or np.isnan(r):
                        return np.nan

                    return r

                # Apply numpy function to arguments
                if self.type == "point":
                    return np_func
                if not isinstance(np_func, tuple):
                    result = np_func(*args)
                else:
                    raise ValueError("Tuple functions not supported in safe_np_func")

                # Apply sanitization to tuple or single result
                if isinstance(result, np.ndarray):
                    sanitized_result = result
                elif isinstance(result, tuple):
                    sanitized_result = tuple(sanitize_result(r) for r in result)
                else:
                    sanitized_result = sanitize_result(result)

                return sanitized_result

            except Exception as e:
                # Comprehensive error handling
                print(f"Error in safe_np_func: {e}")

        if self.show_surface or self.type == "point":
            self.update_surface(safe_np_func, widget.renderer, global_bounds)
            if self.surface_actor:
                self.surface_actor.SetVisibility(self.show_surface)
        if self.show_lines:
            self.update_lines(safe_np_func, widget.renderer, global_bounds)
        if self.show_contour:
            self.update_contour(safe_np_func, widget.renderer, global_bounds)
        widget.vtk_widget.get_render_window().Render()

    def get_bounds(self, widget):
        if self.type == "parametric-1" or self.type == "parametric-2":
            return (
                widget.global_x_min,
                widget.global_x_max,
                widget.global_y_min,
                widget.global_y_max,
                widget.global_z_min,
                widget.global_z_max,
            )

        x_min = (
            widget.global_x_min
            if abs(widget.global_x_min) < abs(self.x_min)
            else self.x_min
        )
        x_max = (
            widget.global_x_max
            if abs(widget.global_x_max) < abs(self.x_max)
            else self.x_max
        )
        y_min = (
            widget.global_y_min
            if abs(widget.global_y_min) < abs(self.y_min)
            else self.y_min
        )
        y_max = (
            widget.global_y_max
            if abs(widget.global_y_max) < abs(self.y_max)
            else self.y_max
        )
        z_min = (
            widget.global_z_min
            if abs(widget.global_z_min) < abs(self.z_min)
            else self.z_min
        )
        z_max = (
            widget.global_z_max
            if abs(widget.global_z_max) < abs(self.z_max)
            else self.z_max
        )
        return (x_min, x_max, y_min, y_max, z_min, z_max)

    def update_surface(self, np_func, renderer, global_bounds):
        if self.surface_actor:
            renderer.RemoveActor(self.surface_actor)
            self.surface_actor = None
        if self.type == "implicit":
            self.surface_actor = create_func_surface_actor(
                np_func,
                global_bounds,
            )
            set_z_gradient_coloring(
                self.surface_actor, self.color_start, self.color_end, self.opacity
            )
        elif self.type == "parametric-2":
            self.surface_actor = create_parametric_func_surface_actor(
                np_func,
                self.u_range,
                self.v_range,
                global_bounds,
                self.color_start,
                self.color_end,
                self.opacity,
            )
        elif self.type == "point":
            self.surface_actor = create_point_actor(
                np_func, self.line_color, self.thickness, self.opacity, global_bounds
            )
        if self.surface_actor:
            renderer.AddActor(self.surface_actor)

    def update_lines(self, np_func, renderer, global_bounds):
        if self.lines_actor:
            renderer.RemoveActor(self.lines_actor)
            self.lines_actor = None
        if self.type == "implicit":
            self.lines_actor = create_func_traces_actor(
                np_func,
                global_bounds,
                self.trace_spacing,
                self.thickness,
                self.line_color,
                self.opacity,
            )
        elif self.type == "parametric-1":
            self.lines_actor = create_parametric_curve_actor(
                np_func,
                self.t_range,
                self.line_color,
                self.thickness,
                self.opacity,
                self.dash_spacing,
                global_bounds,
            )
        elif self.type == "parametric-2":
            self.lines_actor = create_parametric_surface_traces_actor(
                np_func,
                self.u_range,
                self.v_range,
                global_bounds,
                self.trace_spacing,
                self.line_color,
                self.thickness,
                self.opacity,
            )
        if self.lines_actor:
            renderer.AddActor(self.lines_actor)

    def update_contour(self, np_func, renderer, global_bounds):
        if self.contour_actor:
            renderer.RemoveActor(self.contour_actor)
            self.contour_actor = None
        if self.type == "implicit":
            self.contour_actor = create_horizontal_contours_actor(
                np_func,
                global_bounds,
                self.trace_spacing,
                self.thickness,
                self.line_color,
                self.opacity,
            )
        elif self.type == "parametric-2":
            self.contour_actor = create_parametric_horizontal_contours_actor(
                np_func,
                self.u_range,
                self.v_range,
                global_bounds,
                self.trace_spacing,
                self.line_color,
                self.thickness,
                self.opacity,
            )
        if self.contour_actor:
            renderer.AddActor(self.contour_actor)

    def __eq__(self, other):
        if isinstance(other, Func):
            if self.text and other.text and self.text.strip() == other.text.strip():
                return True
            if self.type == "implicit" and other.type == "implicit":
                func1 = sp.simplify(sp.expand(self.func))
                func2 = sp.simplify(sp.expand(other.func))
                return str(func1) == str(func2)
            elif isinstance(self.func, MatrixBase) and isinstance(
                other.func, MatrixBase
            ):
                if (
                    # not sp.simplify(self.func - other.func) == sp.Matrix([0, 0, 0])
                    not self.func == other.func
                    and not self.str.strip() == other.str.strip()
                ):
                    return False
                return True
        return False

    def __hash__(self):
        return hash(str(str(sp.simplify(sp.expand(self.func)))))

    def __str__(self):
        return self.str

    def marshalize(self):
        return {
            "text": self.text,
            "x_min": self.x_min,
            "x_max": self.x_max,
            "y_min": self.y_min,
            "y_max": self.y_max,
            "z_min": self.z_min,
            "z_max": self.z_max,
            "t_range": self.t_range,
            "u_range": self.u_range,
            "v_range": self.v_range,
            "t_range_bounds": self.t_range_bounds,
            "u_range_bounds": self.u_range_bounds,
            "v_range_bounds": self.v_range_bounds,
            "trace_spacing": self.trace_spacing,
            "trace_spacing_bounds": self.trace_spacing_bounds,
            "thickness": self.thickness,
            "thickness_bounds": self.thickness_bounds,
            "dash_spacing": self.dash_spacing,
            "dash_spacing_bounds": self.dash_spacing_bounds,
            "opacity": self.opacity,
            "color_start": [
                self.color_start.GetRed(),
                self.color_start.GetGreen(),
                self.color_start.GetBlue(),
            ],
            "color_end": [
                self.color_end.GetRed(),
                self.color_end.GetGreen(),
                self.color_end.GetBlue(),
            ],
            "line_color": [
                self.line_color.GetRed(),
                self.line_color.GetGreen(),
                self.line_color.GetBlue(),
            ],
            "legal": self.legal,
            "type": self.type,
            "show_surface": self.show_surface,
            "show_lines": self.show_lines,
            "show_contour": self.show_contour,
        }

    def unmarshalize(self, data):
        self.text = data["text"]
        self.x_min = data["x_min"]
        self.x_max = data["x_max"]
        self.y_min = data["y_min"]
        self.y_max = data["y_max"]
        self.z_min = data["z_min"]
        self.z_max = data["z_max"]
        self.t_range = data["t_range"]
        self.u_range = data["u_range"]
        self.v_range = data["v_range"]
        self.t_range_bounds = data["t_range_bounds"]
        self.u_range_bounds = data["u_range_bounds"]
        self.v_range_bounds = data["v_range_bounds"]
        self.trace_spacing = data["trace_spacing"]
        self.trace_spacing_bounds = data["trace_spacing_bounds"]
        self.thickness = data["thickness"]
        self.thickness_bounds = data["thickness_bounds"]
        self.dash_spacing = data["dash_spacing"]
        self.dash_spacing_bounds = data["dash_spacing_bounds"]
        self.opacity = data["opacity"]
        self.color_start = vtk.vtkColor3d(data["color_start"])
        self.color_end = vtk.vtkColor3d(data["color_end"])
        self.line_color = vtk.vtkColor3d(data["line_color"])
        self.legal = data["legal"]
        self.type = data["type"]
        self.show_surface = data["show_surface"]
        self.show_lines = data["show_lines"]
        self.show_contour = data.get("show_contour", False)
        self.parse_function()
        return self
