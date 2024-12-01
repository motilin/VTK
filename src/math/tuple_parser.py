import re
import sympy as sp

class TupleVector:
    def __init__(self, *elements):
        self.elements = elements
    
    def __add__(self, other):
        if isinstance(other, TupleVector):
            return TupleVector(*[a + b for a, b in zip(self.elements, other.elements)])
        return NotImplemented
    
    def __sub__(self, other):
        if isinstance(other, TupleVector):
            return TupleVector(*[a - b for a, b in zip(self.elements, other.elements)])
        return NotImplemented
    
    def __mul__(self, scalar):
        return TupleVector(*[scalar * x for x in self.elements])
    
    def __rmul__(self, scalar):
        return self.__mul__(scalar)
    
    def __div__(self, scalar):
        return TupleVector(*[x / scalar for x in self.elements])
    
    def __truediv__(self, scalar):
        return TupleVector(*[x / scalar for x in self.elements])
    
    def __floordiv__(self, scalar):
        return TupleVector(*[x // scalar for x in self.elements])
    
    def __repr__(self):
        return f"({', '.join(map(str, self.elements))})"
    
    def __str__(self):
        return f"({', '.join(map(str, self.elements))})"
    
    # Function to convert complex string such as "a(b+c,d,e)+(f,g,h)-i(1,2,3)" to TupleVector
    def string_to_tuple_vector(self, string):
        # Regular expression to find 3D tuples with preceding sign and symbol/number
        pattern = re.compile(r'([+-]?\s*[\w\d\.]*\*?\s*|\([^\)]+\)\s*\*?\s*)?\(([^,]+),([^,]+),([^)]+)\)')
        matches = pattern.findall(string)
        
        # Convert matches to TupleVector
        tuple_vectors = []
        for match in matches:
            sign_symbol = match[0].strip()
            elements = [sp.sympify(element.strip()) for element in match[1:]]
            tuple_vector = TupleVector(*elements)
            
            # Process the preceding sign and symbol/number
            if sign_symbol:
                sign_symbol = sign_symbol.replace(' ', '')
                sign_symbol = sign_symbol.replace('*', '')
                if sign_symbol.startswith('-'):
                    sign = -1
                    sign_symbol = sign_symbol[1:]
                else:
                    sign = 1
                    if sign_symbol.startswith('+'):
                        sign_symbol = sign_symbol[1:]
                
                if sign_symbol:
                    scalar = sp.sympify(sign_symbol)
                    tuple_vector = scalar * tuple_vector
                tuple_vector = sign * tuple_vector
            
            tuple_vectors.append(tuple_vector)
        
        return tuple_vectors 


# Test string_to_tuple_vector with extended units
# t_extended = TupleVector().string_to_tuple_vector("-2.05*(b+c,d,e)+3*(f,g,h)-2(1,2,3)+a(4,5,6)")
# t_extended = TupleVector().string_to_tuple_vector("x^2+y^2-z^2-1")
# print(t_extended)

# Sum the tuple vectors with an initial value of TupleVector(0, 0, 0)
# result_sum = sum(t_extended, TupleVector(0, 0, 0))
# print(str(result_sum))