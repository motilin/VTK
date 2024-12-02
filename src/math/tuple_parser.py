import re
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
    function_exponentiation,
    split_symbols,
)

# Define the transformations to apply to the expression
TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
    function_exponentiation,
    split_symbols,
)


class TupleVector:
    def __init__(self, *elements):
        self.elements = tuple(elements)

    def __add__(self, other):
        if isinstance(other, TupleVector):
            return TupleVector(*[a + b for a, b in zip(self.elements, other.elements)])
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, TupleVector):
            return TupleVector(*[a - b for a, b in zip(self.elements, other.elements)])
        return NotImplemented

    def __mul__(self, scalar):
        # Ensure scalar multiplication works with symbolic variables
        try:
            return TupleVector(*[scalar * x for x in self.elements])
        except TypeError:
            # Fallback for cases where direct multiplication fails
            return TupleVector(*[sp.simplify(scalar * x) for x in self.elements])

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __truediv__(self, scalar):
        return TupleVector(*[x / scalar for x in self.elements])

    def __repr__(self):
        return f"({', '.join(map(str, self.elements))})"

    def __str__(self):
        return f"({', '.join(map(str, self.elements))})"

    def __len__(self):
        return len(self.elements)

    def clear_whitespace(self, string):
        return string.replace(" ", "")

    def split_string_on_plus_minus(self, string):
        """
        Split a string on plus and minus signs, respecting parenthesis nesting.

        Args:
            string (str): Input string to be split

        Returns:
            list: List of substrings split at top-level plus/minus signs
        """
        result = []
        current_substring = ""
        paren_level = 0

        for char in string:
            if char == "(":
                paren_level += 1
                current_substring += char
            elif char == ")":
                paren_level -= 1
                current_substring += char
            elif (char == "+" or char == "-") and paren_level == 0:
                # If we're at top-level and encounter +/-, start a new substring
                if current_substring:
                    result.append(current_substring)
                current_substring = char
            else:
                current_substring += char

        # Add the last substring
        if current_substring:
            result.append(current_substring)

        return result

    def find_matching_paren(self, s, start):
        stack = []
        for i in range(start, len(s)):
            if s[i] == "(":
                stack.append("(")
            elif s[i] == ")":
                stack.pop()
                if not stack:
                    return i
        return -1

    def is_valid_tuple(self, s):
        # Check if the string contains exactly two commas
        if not s.count(",") == 2:
            return False
        # Check that all the elements of the tuple are non-empty
        elements = s[1:-1].split(",")
        return all(elements)

    def find_valid_tuple(self, string):
        start = 0
        while start < len(string):
            start = string.find("(", start)
            if start == -1:
                break

            end = self.find_matching_paren(string, start)
            if end == -1:
                break

            tuple_str = string[start : end + 1]
            if self.is_valid_tuple(tuple_str):
                before = string[:start]
                after = string[end + 1 :]
                return before, tuple_str, after

            start += 1

        return None, None, None

    def split_string_around_tuple(self, string):
        before, tuple_str, after = self.find_valid_tuple(string)
        if not tuple_str:
            return None
        return [before, tuple_str, after]

    def from_string(self, tuple_string):
        tuple_string = tuple_string.strip()
        _, tuple_str, _ = self.find_valid_tuple(tuple_string)

        if tuple_str:
            # Remove the parentheses
            tuple_str = tuple_str[1:-1]
            # Split the elements
            elements = tuple_str.split(",")
            elements = [self.parse_element(element) for element in elements]
            # Convert the elements to float and create a TupleVector object
            return TupleVector(*elements)
        else:
            raise ValueError("Invalid 3D tuple string")

    def parse_element(self, element):
        if element.strip() == "+":
            element = "1"
        elif element.strip() == "-":
            element = "-1"
        # Parse the expression and return the result
        return parse_expr(element, transformations=TRANSFORMATIONS)

    def multiply_surroundings(self, tuple_list):
        # Parse the tuple part
        tuple_vector = self.from_string(tuple_list[1])
        self.elements = tuple_vector.elements

        # Process the prefix
        prefix = tuple_list[0].strip()
        # prefix = self.clear_whitespace(prefix)
        if prefix.endswith("*"):
            prefix = prefix[:-1]
        if prefix:
            prefix_value = self.parse_element(prefix)
            self.elements = (prefix_value * self).elements

        # Process the suffix
        suffix = tuple_list[2].strip()
        # suffix = self.clear_whitespace(suffix)
        if suffix.startswith("/"):
            suffix = suffix[1:]
            if suffix:
                suffix_value = self.parse_element(suffix)
                self.elements = (self / suffix_value).elements
        elif suffix.startswith("*"):
            suffix = suffix[1:]
            if suffix:
                suffix_value = self.parse_element(suffix)
                self.elements = (suffix_value * self).elements
        elif suffix:
            suffix_value = self.parse_element(suffix)
            self.elements = (suffix_value * self).elements

    def parse(self, string):
        substrings = self.split_string_on_plus_minus(string)
        result_vector = TupleVector(0, 0, 0)
        for substring in substrings:
            tuple_list = self.split_string_around_tuple(substring)
            if tuple_list:
                self.multiply_surroundings(tuple_list)
            result_vector += self
        self.elements = result_vector.elements


### Tests ###


def test_clear_whitespace():
    string = "3 + 5 - 2 + 8"
    tv = TupleVector()
    new_string = tv.clear_whitespace(string)
    assert new_string == "3+5-2+8"


def test_split_string_on_plus_minus():
    string = "3 + 5 - 2 + 8"
    tv = TupleVector()
    substrings = tv.split_string_on_plus_minus(string)
    assert substrings == ["3 ", "+ 5 ", "- 2 ", "+ 8"]

    string = "(d,a,b)-(t/(1+a^2))(b+2,c/3,4)/d + (a,b,c) - t(5,4,3)"
    tv = TupleVector()
    substrings = tv.split_string_on_plus_minus(string)
    assert substrings == [
        "(d,a,b)",
        "-(t/(1+a^2))(b+2,c/3,4)/d ",
        "+ (a,b,c) ",
        "- t(5,4,3)",
    ]


def test_split_string_around_tuple():
    tv = TupleVector()

    string = "3 + (1, 2, 3) - 2 + 8"
    substrings = tv.split_string_around_tuple(string)
    assert substrings == ["3 + ", "(1, 2, 3)", " - 2 + 8"]

    string = "(t^2/a)(a,b,c)/b^2"
    substrings = tv.split_string_around_tuple(string)
    assert substrings == ["(t^2/a)", "(a,b,c)", "/b^2"]

    string = "(a,b,c)"
    substrings = tv.split_string_around_tuple(string)
    assert substrings == ["", "(a,b,c)", ""]

    string = "t/2(,b,c)9"
    substrings = tv.split_string_around_tuple(string)
    assert substrings == None

    string = "+ t(-1,1,a(2+a))/(1+a)^2"
    substrings = tv.split_string_around_tuple(string)
    assert substrings == ["+ t", "(-1,1,a(2+a))", "/(1+a)^2"]


def test_from_string():
    tv = TupleVector()

    tuple_string = "(1,2,3)"
    tuple_vector = tv.from_string(tuple_string)
    assert tuple_vector.elements == (1.0, 2.0, 3.0)

    tuple_string = "(1.5,2.5,3.5)"
    tuple_vector = tv.from_string(tuple_string)
    assert tuple_vector.elements == (1.5, 2.5, 3.5)

    try:
        tuple_string = "(1,,3)"
        tv.from_string(tuple_string)
    except ValueError as e:
        assert str(e) == "Invalid 3D tuple string"

    b, c = sp.symbols("b c")
    tuple_string = "(t^2/a,b,c)"
    tuple_vector = tv.from_string(tuple_string)
    assert tuple_vector.elements == (sp.sympify("t**2/a"), b, c)


def test_multiply_surroundings():
    tv = TupleVector()

    tuple_list = ["3 * ", "(1,2,3)", " / 2"]
    tv.multiply_surroundings(tuple_list)
    assert tv.elements == (1.5, 3.0, 4.5)

    tuple_list = ["2 * ", "(1,2,3)", " * 3"]
    tv.multiply_surroundings(tuple_list)
    assert tv.elements == (6.0, 12.0, 18.0)

    tuple_list = ["", "(1,2,3)", " * 4"]
    tv.multiply_surroundings(tuple_list)
    assert tv.elements == (4.0, 8.0, 12.0)

    tuple_list = ["5 * ", "(1,2,3)", ""]
    tv.multiply_surroundings(tuple_list)
    assert tv.elements == (5.0, 10.0, 15.0)

    a, b, c, t = sp.symbols("a b c t")
    tuple_list = ["t^2/a", "(a,b,c)", "/(b^2/c)"]
    tv.multiply_surroundings(tuple_list)
    assert tv.elements == (
        t**2 * c / b**2,
        t**2 * c / (a * b),
        t**2 * c**2 / (a * b**2),
    )


def test_parse():
    tv = TupleVector()

    string = "3 * (1,2,3) / 2 + 2 * (4,5,6) * 3"
    tv.parse(string)
    expected = (1.5 + 24, 3.0 + 30, 4.5 + 36)
    assert tv.elements == expected

    string = "t^2/a * (a,b,c) / (b^2/c) + (1,1,1)"
    tv.parse(string)
    a, b, c, t = sp.symbols("a b c t")
    expected = (
        t**2 * c / b**2 + 1,
        t**2 * c / (a * b) + 1,
        t**2 * c**2 / (a * b**2) + 1,
    )
    assert tv.elements == expected

    string = "(d,a,b)-(t/(1+a^2))(b+2,c/3,4)/d + (a,b,c) - t(5,4,3)"
    tv.parse(string)
    a, b, c, d, t = sp.symbols("a b c d t")
    expected = (
        d - t / (1 + a**2) * (b + 2) / d + a - 5 * t,
        a - t / (1 + a**2) * (c / 3) / d + b - 4 * t,
        b - t / (1 + a**2) * (4) / d + c - 3 * t,
    )
    assert tv.elements == expected

    tv = TupleVector()
    string = "x^2+y^2+z^2-1"
    tv.parse(string)
    assert len(tv) == 0

    string = "(a,b,c)"
    tv.parse(string)
    a, b, c = sp.symbols("a b c")
    assert tv.elements == (a, b, c)

    string = "(1,2,3)"
    tv.parse(string)
    assert tv.elements == (1, 2, 3)

    string = "(1/(1+a))(1,a,a^2) + t(-1,1,a(2+a))/(1+a)^2"
    tv.parse(string)
    a, t = sp.symbols("a t")
    expected = (
        1 / (1 + a) + t * (-1) / (1 + a) ** 2,
        a / (1 + a) + t * 1 / (1 + a) ** 2,
        a**2 / (1 + a) + t * a * (2 + a) / (1 + a) ** 2,
    )
    assert tv.elements == expected

    string = "(a*sin(a), exp(a) cos(a), sin(a) cos(a)) + t(a*cos(a)+sin(a) , exp(a)(cos(a)-sin(a)),cos(2a)) / sqrt((a*cos(a)+sin(a))^2 + (exp(a)(cos(a)-sin(a)))^2 + (cos(2a))^2)"
    tv.parse(string)
    a, t = sp.symbols("a t")
    expected = (
        a*sp.sin(a) + t*(a*sp.cos(a) + sp.sin(a)) / sp.sqrt((a*sp.cos(a) + sp.sin(a))**2 + (sp.exp(a)*(sp.cos(a) - sp.sin(a)))**2 + (sp.cos(2*a))**2), # type: ignore
        sp.exp(a)*sp.cos(a) + t*(sp.exp(a)*(sp.cos(a) - sp.sin(a))) / sp.sqrt((a*sp.cos(a) + sp.sin(a))**2 + (sp.exp(a)*(sp.cos(a) - sp.sin(a)))**2 + (sp.cos(2*a))**2), # type: ignore
        sp.sin(a)*sp.cos(a) + t*sp.cos(2*a) / sp.sqrt((a*sp.cos(a) + sp.sin(a))**2 + (sp.exp(a)*(sp.cos(a) - sp.sin(a)))**2 + (sp.cos(2*a))**2), # type: ignore
    )
    assert tv.elements == expected
    
    string = "(t sin(a), t cos(a), t)"
    tv.parse(string)
    a, t = sp.symbols("a t")
    expected = (
        t*sp.sin(a),
        t*sp.cos(a),
        t,
    )
    assert tv.elements == expected


if __name__ == "__main__":
    test_clear_whitespace()
    test_split_string_on_plus_minus()
    test_split_string_around_tuple()
    test_from_string()
    test_multiply_surroundings()
    test_parse()
    print("All tests passed!")
