def parse_function(text):
    try:
        func_code = f"""
def custom_function(a, b, c):                    
    return lambda x, y, z: {text}
        """
        exec(func_code, globals())
        func = globals()['custom_function']
        return func
    except (SyntaxError, NameError, TypeError) as e:
        print(f"Error: {e}")
        return None
