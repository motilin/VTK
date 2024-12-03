def is_valid_tuple_start(input_string, index):
    """
    Determine if the parenthesis at the given index starts a valid tuple.

    Checks the context before the opening parenthesis to ensure it's a tuple.

    Args:
        input_string (str): The full input string
        index (int): Index of the opening parenthesis

    Returns:
        bool: Whether the parenthesis begins a valid tuple
    """
    # If at the start of string, it could be a tuple
    if index == 0:
        return True

    # Check preceding character
    prev_char = input_string[index - 1]

    # Tuple starts after these characters or at the start of an expression
    invalid_preceding_chars = set(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_)"
    )

    # Allow tuples that are preceded by function names or other valid characters
    return prev_char not in invalid_preceding_chars or prev_char.isalpha()


def replace_tuples_with_matrix(input_string):
    """
    Replace tuples in a string with Matrix notation.

    Carefully identifies and replaces tuples while maintaining
    the integrity of nested expressions.

    Args:
        input_string (str): The input string containing potential tuples

    Returns:
        str: The string with tuples replaced by Matrix notation
    """
    if not input_string or not isinstance(input_string, str):
        return input_string

    result = []
    i = 0
    length = len(input_string)

    while i < length:
        # Potential tuple detection
        if input_string[i] == "(" and is_valid_tuple_start(input_string, i):
            # Start of potential tuple detection
            tuple_start = i
            parentheses_level = 1
            comma_count = 0
            j = i + 1

            # Scan to determine if this is a genuine tuple
            while j < length and parentheses_level > 0:
                if input_string[j] == "(":
                    parentheses_level += 1
                elif input_string[j] == ")":
                    parentheses_level -= 1
                elif input_string[j] == "," and parentheses_level == 1:
                    comma_count += 1

                j += 1

            # Confirmed tuple if we have at least one comma and balanced parentheses
            if parentheses_level == 0 and comma_count > 0:
                tuple_content = input_string[tuple_start + 1 : j - 1]
                result.append(f" Matrix([{tuple_content}]) ")
                i = j
            else:
                # Not a tuple, append original characters
                result.append(input_string[i])
                i += 1
        else:
            result.append(input_string[i])
            i += 1

    return "".join(result)


# Comprehensive test cases
def test_tuple_replacement():
    test_cases = [
        ("(sin(u),cos(v),u)", " Matrix([sin(u),cos(v),u]) "),
        ("f(x) + (1,2,3) * g(y)", "f(x) + " + " Matrix([1,2,3]) " + " * g(y)"),
        ("No tuples here", "No tuples here"),
        ("math.func(x, (1,2,3))", "math.func Matrix([x, (1,2,3)]) "),
        ("(1,2,3,4)", " Matrix([1,2,3,4]) "),
        ("t(1,1,1)", "t Matrix([1,1,1]) "),
        ("complex((1,2), (3,4))", "complex Matrix([(1,2), (3,4)]) "),
    ]

    for input_str, expected in test_cases:
        result = replace_tuples_with_matrix(input_str)
        assert (
            result == expected
        ), f"Failed for input {input_str}: got {result}, expected {expected}"

    print("All tuple replacement tests passed!")


# Run tests
test_tuple_replacement()


if __name__ == "__main__":
    test_tuple_replacement()
