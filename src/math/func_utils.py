import re
from numpy import (
    pi,
    sin,
    cos,
    tan,
    sqrt,
    exp,
    log,
    sinh,
    cosh,
    tanh,
    arcsin,
    arccos,
    arctan,
    arcsinh,
    arccosh,
    arctanh,
)

def parse_function(text):
    text = text.replace("^", "**")
    text = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', text)
    try:
        func_code = f"""
def custom_function(a, b, c):                    
    return lambda x, y, z: {text}
        """
        exec(func_code, globals())
        func = globals()['custom_function']
        return func
    except Exception as e:
        print(f"Error: {e}")
        return None

