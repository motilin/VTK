import re, ast, astor, rich, sympy as sp
from sympy import symbols, Matrix, Abs, simplify
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
    function_exponentiation,
    split_symbols,
)

TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
    function_exponentiation,
    split_symbols,
)

### Custom functions


def is_legal_1d_vector(vector):
    if not isinstance(vector, Matrix) and vector.shape[0] != 3:
        return False
    t = symbols("t")
    if t not in vector.free_symbols:
        return False
    return True


# Define a vector
def m(*args):
    return Matrix(args)


def norm(vector):
    t = symbols("t")
    norm = 0
    for i in range(len(vector)):
        norm += vector[i] ** 2
        norm = norm.simplify()
    return (norm**0.5).simplify()


def simplify_vector(vector):
    t = symbols("t")
    return Matrix([v.simplify() for v in vector])


def remove_abs(expr):
    def _remove_abs_recursively(e):
        # Handle basic types and atomic expressions
        if not hasattr(e, "func") or not hasattr(e, "args"):
            return e

        # Special handling for Abs
        if e.func == Abs:
            return _remove_abs_recursively(e.args[0])

        # Recursive handling of arguments
        try:
            new_args = [_remove_abs_recursively(arg) for arg in e.args]
            return e.func(*new_args)
        except Exception:
            # Fallback if argument reconstruction fails
            return e

    # Apply recursive removal
    try:
        # First, remove Abs
        expr_without_abs = _remove_abs_recursively(expr)

        # Then simplify with real assumptions
        t = symbols("t", real=True)
        expr_without_abs = simplify(expr_without_abs)

        return expr_without_abs
    except Exception as ex:
        print(f"Error in remove_abs: {ex}")
        return expr


def remove_abs_vector(vector):
    no_abs = [remove_abs(v) for v in vector]
    simplified = [v.simplify() for v in no_abs]
    return Matrix(simplified)


# Create a curvature function
def curvature(vector):
    if not is_legal_1d_vector(vector):
        raise ValueError("Invalid vector in curvature()")
    t = symbols("t")
    v1 = simplify_vector(vector.diff(t))
    v2 = simplify_vector(v1.diff(t))
    k = v1.cross(v2).norm() / v1.norm() ** 3
    rich.print(f"k = {sp.sstr(k.simplify())}")
    return Matrix([t, k, 0])


def T(r):
    if not is_legal_1d_vector(r):
        raise ValueError("Invalid vector in T()")
    t = symbols("t")
    dr = simplify_vector(r.diff(t))
    T = dr / norm(dr)
    T = remove_abs_vector(T)
    T = simplify_vector(T)
    rich.print(f"T(t) = {sp.sstr(T)}")
    return T


def N(r):
    if not is_legal_1d_vector(r):
        raise ValueError("Invalid vector in N()")
    t = symbols("t")
    dr = simplify_vector(r.diff(t))
    T = dr / norm(dr)
    dT = simplify_vector(T.diff(t))
    N = dT / dT.norm()
    N = remove_abs_vector(N)
    N = simplify_vector(N)
    rich.print(f"N(t) = {sp.sstr(N)}")
    return N


def B(r):
    if not is_legal_1d_vector(r):
        raise ValueError("Invalid vector in B()")
    t = symbols("t")
    dr = simplify_vector(r.diff(t))
    T = dr / norm(dr)
    dT = simplify_vector(T.diff(t))
    N = dT / norm(dT)
    T = remove_abs_vector(T)
    T = simplify_vector(T)
    N = remove_abs_vector(N)
    N = simplify_vector(N)
    B = T.cross(N)
    B = simplify_vector(B)
    rich.print(f"B(t) = {sp.sstr(B)}")
    return B


CUSTOM_FUNCTIONS = {
    "m": m,
    "curvature": curvature,
    "T": T,
    "N": N,
    "B": B,
    "norm": norm,
}


def preprocess_implicit_multiplication(expr_str):
    """
    Preprocess expression to handle implicit multiplication.
    For instance, convert "2x" to "2*x", "2(x+1)" to "2*(x+1)", "2sin(x)" to "2*sin(x)" or "a b c" to "a*b*c".
    Leaves alone expressions such as "func(1,2,3)" or "abc" that may represent function calls or variable names.

    Args:
        expr_str (str): The original expression string
    Returns:
        str: Expression with implicit multiplication made explicit
    """
    # Trim whitespace
    expr_str = expr_str.strip()

    # Skip if empty string
    if not expr_str:
        return expr_str

    # Rules for implicit multiplication
    patterns = [
        # Space between alphanumeric tokens: "a b c" -> "a*b*c"
        (r"([a-zA-Z0-9])\s+([a-zA-Z0-9])", r"\1*\2"),
        # Number followed by letter: "2x" -> "2*x"
        (r"(\d+)([a-zA-Z])", r"\1*\2"),
        # Letter preceded by number: "x2" -> "x*2"
        (r"([a-zA-Z])(\d+)", r"\1*\2"),
        # Closing parenthesis followed by an alphanumeric token: "(x+1) 2" -> "(x+1)*2"
        (r"(\))\s*([a-zA-Z0-9])", r"\1*\2"),
        # Alphanumeric token followed by opening parenthesis with whitespace: "x (y+1)" -> "x*(y+1)"
        (r"([a-zA-Z0-9])\s+(\()", r"\1*\2"),
    ]

    # Apply each pattern sequentially
    for pattern, repl in patterns:
        expr_str = re.sub(pattern, repl, expr_str)

    return expr_str


def transform_func_calls(expr_str, custom_funcs):
    """
    Transform custom function calls in an expression string using AST.

    Args:
        expr_str (str): The expression string to transform
        custom_funcs (dict): Dictionary mapping function names to their implementations

    Returns:
        str: Transformed expression string with function calls evaluated
    """

    expr_str = preprocess_implicit_multiplication(expr_str)

    class FuncCallTransformer(ast.NodeTransformer):
        def visit_Call(self, node):
            # Check if this is a call to one of our custom functions
            if isinstance(node.func, ast.Name) and node.func.id in custom_funcs:

                # Recursively transform arguments
                transformed_args = []
                for arg in node.args:
                    transformed_arg = self.visit(arg)
                    transformed_args.append(transformed_arg)

                pass

                # Evaluate arguments
                try:
                    # Compile arguments to values
                    arg_strs = [
                        astor.to_source(arg).strip() for arg in transformed_args
                    ]
                    args = [
                        parse_expr(arg_str, transformations=TRANSFORMATIONS)
                        for arg_str in arg_strs
                    ]
                    # Call the custom function
                    result = custom_funcs[node.func.id](*args)

                    # Convert result back to AST node
                    return ast.Constant(value=result)

                except Exception as e:
                    # If evaluation fails, return original node
                    print(f"Evaluation of {node.func.id} failed: {e}")
                    return node

            # For other function calls, continue traversing
            return self.generic_visit(node)

    # Parse the expression into an AST
    tree = ast.parse(expr_str, mode="eval")

    # Transform the AST
    transformer = FuncCallTransformer()
    modified_tree = transformer.visit(tree)

    # Convert back to a string
    return astor.to_source(modified_tree).strip()


def parse(expr_str):
    # Transform the expression
    transformed_expr = transform_func_calls(expr_str, CUSTOM_FUNCTIONS)

    try:
        expr = parse_expr(
            transformed_expr,
            transformations=TRANSFORMATIONS,
        )
    except Exception as e:
        print(f"Error parsing expression: {e}")
        return None

    return expr


if __name__ == "__main__":
    # Test cases
    print(parse("func(1,2,3)"))  # Should print 6
    print(parse("func(1+2, 3*4, 5**2)"))  # More complex example
    print(parse("x + func(1,2,3)"))  # Mixed expression


