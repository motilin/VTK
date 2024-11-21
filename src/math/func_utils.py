import re, copy
import numpy as np
from numpy import (
    sin,
    cos,
    tan,
    arcsin,
    arccos,
    arctan,
    sinh,
    cosh,
    tanh,
    exp,
    log,
    log10,
    sqrt,
    pi,
)

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
)
from src.utils.line_utils import create_func_traces_actor, create_parametric_curve_actor
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
    function_exponentiation,
    split_symbols,
)


class Func:
    def __init__(self, text):
        self.text = text
        self.x_min, self.x_max = X_MIN, X_MAX
        self.y_min, self.y_max = Y_MIN, Y_MAX
        self.z_min, self.z_max = Z_MIN, Z_MAX
        self.u_range = (0, 1)
        self.v_range = (0, 1)
        self.trace_spacing = 1
        self.trace_spacing_bounds = DEFAULT_SLIDER_BOUNDS
        self.thickness = 1
        self.dash_spacing = 0
        self.opacity = 1
        self.color_start = DEFAULT_COLOR_START
        self.color_end = DEFAULT_COLOR_END
        self.line_color = DEFAULT_LINE_COLOR
        self.legal = False
        self.type = None
        self.show_surface = False
        self.show_lines = True
        self.transformations = standard_transformations + (
            implicit_multiplication_application,
            convert_xor,
            function_exponentiation,
            split_symbols,
        )
        self.func = sp.Basic()
        self.coeffs = set()
        self.surface_actor = None
        self.lines_actor = None
        self.parse_function()

    def parse_function(self):
        try:
            expr = parse_expr(
                self.text, evaluate=False, transformations=self.transformations
            )
            if isinstance(expr, sp.Equality):
                expr = sp.simplify(expr.lhs) - sp.simplify(expr.rhs)
            self.func = expr

            if isinstance(expr, tuple):
                if len(expr) == 3:
                    u, v = sp.symbols("u v")
                    all_symbols = set.union(*[e.free_symbols for e in expr])
                    self.coeffs = all_symbols - {u, v}
                    self.latex = expr.__str__()
                    self.legal = True
                    self.type = "parametric"

            elif isinstance(exp, sp.Basic):
                x, y, z = sp.symbols("x y z")
                self.coeffs = expr.free_symbols - {x, y, z}
                self.latex = sp.latex(expr)
                self.legal = True
                self.type = "implicit"

        except Exception as e:
            print(e)
            self.legal = False

    def update_render(self, widget):
        func = copy.copy(self.func)
        global_bounds = self.get_bounds(widget)

        # Replace coefficients with values
        for coeff in self.coeffs:
            if coeff in widget.coeffs:
                if isinstance(func, sp.Basic):
                    func = func.subs(coeff, widget.coeffs[coeff])
                elif isinstance(func, tuple):
                    func = tuple([f.subs(coeff, widget.coeffs[coeff]) for f in func])
            else:
                raise ValueError(f"Missing coefficient: {coeff}")

        # Create a numpy function from the sympy function
        if isinstance(func, sp.Basic):
            x, y, z = sp.symbols("x y z")
            np_func = sp.lambdify((x, y, z), func, "numpy")
        elif isinstance(func, tuple):
            u, v = sp.symbols("u v")
            np_func = sp.lambdify((u, v), func, "numpy")

        if self.show_surface:
            self.update_surface(np_func, widget.renderer, global_bounds)
        if self.show_lines:
            self.update_lines(np_func, widget.renderer, global_bounds)
        widget.vtk_widget.get_render_window().Render()

    def get_bounds(self, widget):
        x_min = (
            widget.global_x_min
            if abs(widget.global_x_min) < abs(self.x_min)
            else self.x_min
        )
        x_max = (
            widget.global_x_max
            if abs(widget.global_x_max) > abs(self.x_max)
            else self.x_max
        )
        y_min = (
            widget.global_y_min
            if abs(widget.global_y_min) < abs(self.y_min)
            else self.y_min
        )
        y_max = (
            widget.global_y_max
            if abs(widget.global_y_max) > abs(self.y_max)
            else self.y_max
        )
        z_min = (
            widget.global_z_min
            if abs(widget.global_z_min) < abs(self.z_min)
            else self.z_min
        )
        z_max = (
            widget.global_z_max
            if abs(widget.global_z_max) > abs(self.z_max)
            else self.z_max
        )
        return (x_min, x_max, y_min, y_max, z_min, z_max)

    def update_surface(self, np_func, renderer, global_bounds):
        if self.surface_actor:
            renderer.RemoveActor(self.surface_actor)
        if self.type == "implicit":
            self.surface_actor = create_func_surface_actor(
                np_func,
                global_bounds,
            )
            set_z_gradient_coloring(
                self.surface_actor, self.color_start, self.color_end
            )
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
            )
        elif self.type == "parametric":
            self.lines_actor = create_parametric_curve_actor(
                np_func,
                self.u_range,
                self.v_range,
                self.line_color,
                self.thickness,
                self.opacity,
                self.dash_spacing,
            )
        else:
            raise ValueError("Invalid function type")
        renderer.AddActor(self.lines_actor)

    def __eq__(self, other):
        if isinstance(other, Func):
            if self.type == "implicit" and other.type == "implicit":
                func1 = sp.simplify(sp.expand(self.func))
                func2 = sp.simplify(sp.expand(other.func))
                return str(func1) == str(func2)
            elif isinstance(self.func, tuple) and isinstance(other.func, tuple):
                for comp1, comp2 in zip(self.func, other.func):
                    if not sp.simplify(comp1 - comp2) == 0:
                        return False
                return True
        return False

    def __hash__(self):
        return hash(str(str(sp.simplify(sp.expand(self.func)))))

    def __str__(self):
        return self.latex
