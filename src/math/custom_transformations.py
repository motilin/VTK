from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
    function_exponentiation,
    split_symbols,
)

from tokenize import NAME, OP, NUMBER, generate_tokens, TokenInfo
from typing import List, Tuple, Dict, Any
from sympy import Matrix, Integer
from io import StringIO

# Define the TOKEN and DICT types
TOKEN = Tuple[int, str]
DICT = Dict[str, Any]


def parentheses_to_matrix2(
    tokens: List[TOKEN], local_dict: DICT, global_dict: DICT
) -> List[TOKEN]:
    result = []
    stack = []
    for tok in tokens:
        # Ignore the ENDMARKER token (type 4)
        if isinstance(tok, int) or (isinstance(tok, tuple) and tok[0] == 4):
            continue

        if tok == (OP, "("):
            stack.append((len(result), []))
        elif tok == (OP, ")") and stack:
            start, group = stack.pop()
            if all(
                t[0] in {NAME, NUMBER, OP} and t[1] != "(" and t[1] != ")"
                for t in group
            ):
                # Check if the group is a comma-separated list
                if any(t[1] == "," for t in group):
                    # Convert to Matrix tokens
                    matrix_tokens = [
                        (NAME, "Matrix"),
                        (OP, "("),
                        (OP, "["),
                    ]
                    for t in group:
                        if t[1] != ",":
                            matrix_tokens.append(t)
                        else:
                            matrix_tokens.append((OP, ","))
                    matrix_tokens.extend(
                        [
                            (OP, "]"),
                            (OP, ")"),
                        ]
                    )
                    result = result[:start] + matrix_tokens
                else:
                    result.extend(group)
            else:
                result.extend(group)
        elif stack:
            stack[-1][1].append(tok)
        else:
            result.append(tok)
    return result


###################


def parentheses_to_matrix(
    tokens: List[TOKEN], local_dict: Dict[str, Any], global_dict: Dict[str, Any]
) -> List[TOKEN]:
    result = []
    stack = []
    for tok in tokens:
        # Ignore ENDMARKER or invalid tokens
        if isinstance(tok, int) or (isinstance(tok, tuple) and tok[0] == 4):
            continue

        if tok == (OP, "("):
            # Start of a potential matrix-like group
            stack.append((len(result), []))
        elif tok == (OP, ")") and stack:
            start, group = stack.pop()

            # Check if group looks like a comma-separated list of numbers
            is_number_list = any(t[1] == "," for t in group) and all(
                t[0] in {NUMBER, OP} and t[1] not in {"(", ")"} for t in group
            )

            if is_number_list:
                # Convert to Matrix tokens
                matrix_tokens = [
                    (NAME, "Matrix"),
                    (OP, "("),
                    (OP, "["),
                    (OP, "["),
                ]

                first = True
                for t in group:
                    if t[1] == ",":
                        # Add comma between elements or add closing/opening brackets
                        if first:
                            matrix_tokens.append(t)
                            first = False
                        else:
                            matrix_tokens.extend(
                                [
                                    (OP, "]"),
                                    (OP, ","),
                                    (OP, "["),
                                ]
                            )
                    else:
                        matrix_tokens.append(t)

                matrix_tokens.extend(
                    [
                        (OP, "]"),
                        (OP, "]"),
                        (OP, ")"),
                    ]
                )

                result = result[:start] + matrix_tokens
            else:
                # If not a number list, keep original tokens
                result.extend(group)
        elif stack:
            # If inside a group, collect tokens
            stack[-1][1].append(tok)
        else:
            # Normal token processing
            result.append(tok)

    return result


##################
## Tests

TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
    function_exponentiation,
    split_symbols,
    parentheses_to_matrix,
)


def test1():
    # Generate tokens for the string "(1,2,3)"
    input_string = "(1,2,3)"
    token_infos = list(generate_tokens(StringIO(input_string).readline))

    # Remove the ENDMARKER token at the end
    token_infos = token_infos[:-1]

    # Convert TokenInfo objects to TOKEN tuples
    tokens = [(token.type, token.string) for token in token_infos]

    # Expected token list after transformation
    expected_tokens = [
        (NAME, "Matrix"),
        (OP, "("),
        (OP, "["),
        (NUMBER, "1"),
        (OP, ","),
        (NUMBER, "2"),
        (OP, ","),
        (NUMBER, "3"),
        (OP, "]"),
        (OP, ")"),
    ]

    # Apply the transformation
    result = parentheses_to_matrix(tokens, {}, {})

    # Assert the result
    assert result == expected_tokens, f"Expected {expected_tokens}, but got {result}"


def test2():
    expr = parse_expr("(1,2,3)", transformations=TRANSFORMATIONS)
    assert expr == Matrix([[1, 2, 3]]), f"Expected Matrix([[1, 2, 3]]), but got {expr}"


if __name__ == "__main__":
    # test1()
    test2()
    print("Done!")


