import re
import sympy as sp

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
    
    def string_to_tuple_vector(self, string):
        # Enhanced regex to capture complex tuples and surrounding operations
        pattern = re.compile(r'((?:[+-]?\s*[\w\d\.]*\*?)?)\s*(\([^()]*(?:\([^()]*\)[^()]*)*\))')
        
        # Find all matches in the string
        matches = pattern.findall(string)
        
        # Process matches into TupleVector objects
        tuple_vectors = []
        
        for match in matches:
            # Clean up the preceding expression
            pre_expr = match[0].strip()
            
            # Extract elements from the tuple (removing outer parentheses)
            tuple_str = match[1][1:-1]  # Remove the first and last parenthesis
            
            # Split elements, handling potential nested expressions
            elements = self._split_tuple_elements(tuple_str)
            
            # Create TupleVector
            current_vector = TupleVector(*[sp.sympify(elem.strip()) for elem in elements])
            
            # Process preceding expression (sign and scalar)
            if pre_expr:
                # Remove any extra spaces and asterisks
                pre_expr = pre_expr.replace(' ', '').replace('*', '')
                
                # Determine sign
                sign = 1
                if pre_expr.startswith('-'):
                    sign = -1
                    pre_expr = pre_expr[1:]
                elif pre_expr.startswith('+'):
                    pre_expr = pre_expr[1:]
                
                # Apply scalar if present
                if pre_expr:
                    scalar = sp.sympify(pre_expr)
                    current_vector = scalar * current_vector
                
                # Apply sign
                current_vector = sign * current_vector
            
            tuple_vectors.append(current_vector)
        
        return tuple_vectors
    
    def _split_tuple_elements(self, tuple_str):
        # Custom splitting that respects nested parentheses
        elements = []
        current_element = []
        paren_count = 0
        
        for char in tuple_str:
            if char == ',' and paren_count == 0:
                # Complete current element
                elements.append(''.join(current_element))
                current_element = []
            else:
                # Track parentheses nesting
                if char == '(':
                    paren_count += 1
                elif char == ')':
                    paren_count -= 1
                
                current_element.append(char)
        
        # Add last element
        if current_element:
            elements.append(''.join(current_element))
        
        return elements

# Example usage and testing
tv = TupleVector(1, 2, 3)
parser = tv.string_to_tuple_vector

# Test cases
test_cases = [
    "(a,b,c)+(d,e,f)-(g,h,i)",
    "2(a,b,c)",
    "x(a,b,c)",
    "((a+2)/b)(c,d,e)",
    "2((a+2)/b)(c,d,e)",
    "(1/(1+a),a/(1+a),a^2/(1+a))"
]

for case in test_cases:
    print(f"Parsing: {case}")
    results = parser(case)
    for result in results:
        print(result)
    print()