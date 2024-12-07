import re, ast, astor, rich, sympy as sp
from sympy import symbols, Matrix
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


# Define a vector
def m(*args):
    return Matrix(args)


# Create a curvature function
def curvature(vector):
    if not isinstance(vector, Matrix):
        raise ValueError("k() expects a Matrix")
    if vector.shape[0] != 3:
        raise ValueError("k() expects a 3D vector")

    t = symbols("t")
    if t not in vector.free_symbols:
        raise ValueError("k() expects a vector with a free variable t")

    v1 = vector.diff(t)
    v2 = v1.diff(t)
    k = v1.cross(v2).norm() / v1.norm() ** 3
    rich.print(f"k = {k.simplify()}")
    rich.print(sp.latex(k.simplify()))
    return Matrix([t, k, 0])


CUSTOM_FUNCTIONS = {"m": m, "curvature": curvature}


def preprocess_implicit_multiplication2(expr_str):
    """
    Preprocess expression to handle implicit multiplication.
    For instance, convert "2x" to "2*x", "2(x+1)" to "2*(x+1)", "2sin(x)" to "2*sin(x)" or "a b c" to "a*b*c".
    Leaves alone expressions such as "func(1,2,3)" or "abc" that may represent function calls or variable names.

    Args:
        expr_str (str): The original expression string

    Returns:
        str: Expression with implicit multiplication made explicit
    """
    pass


import re


def preprocess_implicit_multiplication(expr_str):
    """
    Preprocess expression to handle implicit multiplication.

    Rules:
    1. Add '*' between space-separated alphanumeric chars
    2. Add '*' between number and character
    3. Add '*' between number and opening parenthesis
    4. Add '*' between closing parenthesis and number

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
        
        # Number followed by opening parenthesis: "2(x+1)" -> "2*(x+1)"
        (r"(\d+)(\()", r"\1*\2"),
        
        # Closing parenthesis followed by an alphanumeric token: "(x+1) 2" -> "(x+1)*2"
        (r"(\))\s*([a-zA-Z0-9])", r"\1*\2"),
        
        # Letter followed by opening parenthesis with whitespace: "x (y+1)" -> "x*(y+1)"
        (r"([a-zA-Z])\s+(\()", r"\1*\2"),
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
