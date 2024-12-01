class TupleExpressionParser:
    def __init__(self):
        # Initialize parsing context and configuration
        self.parsing_context = {
            'current_token': None,
            'token_stream': [],
            'error_log': [],
            'nested_level': 0
        }
    
    def tokenize(self, expression):
        """
        Advanced tokenization strategy
        
        Breaks down input expression into meaningful tokens:
        - Identifies scalars, tuples, operators
        - Handles nested structures
        - Preserves mathematical semantics
        """
        tokens = []
        current_token = ''
        in_tuple = False
        nested_depth = 0
        
        for char in expression:
            if char == '(':
                nested_depth += 1
                in_tuple = True
                current_token += char
            elif char == ')':
                nested_depth -= 1
                current_token += char
                if nested_depth == 0:
                    in_tuple = False
            elif char in ['+', '-', '*'] and not in_tuple:
                # Operator handling
                if current_token:
                    tokens.append(current_token)
                tokens.append(char)
                current_token = ''
            else:
                current_token += char
        
        if current_token:
            tokens.append(current_token)
        
        return tokens
    
    def parse_tuple_expression(self, tokens):
        """
        Recursive descent parsing of tuple expressions
        
        Core parsing strategy with multi-level parsing:
        - Handles scalar multiplication
        - Manages tuple additions/subtractions
        - Supports nested tuple structures
        """
        def parse_scalar_tuple(tokens):
            """Parse scalar * tuple multiplication"""
            result = []
            i = 0
            while i < len(tokens):
                if isinstance(tokens[i], str) and tokens[i].startswith('('):
                    # Tuple handling
                    tuple_contents = tokens[i][1:-1].split(',')
                    if i > 0 and isinstance(tokens[i-1], (int, float, str)):
                        # Scalar multiplication
                        scalar = tokens[i-1]
                        transformed_tuple = [f"{scalar}*{item.strip()}" for item in tuple_contents]
                        result.extend(transformed_tuple)
                    else:
                        result.extend(tuple_contents)
                else:
                    result.append(tokens[i])
                i += 1
            return result
        
        def combine_expressions(parsed_tokens):
            """Combine parsed tokens into final expression"""
            combined = []
            current_expr = []
            current_op = '+'
            
            for token in parsed_tokens:
                if token in ['+', '-']:
                    current_op = token
                else:
                    if current_op == '+':
                        current_expr.append(token)
                    elif current_op == '-':
                        current_expr.append(f'-{token}')
            
            return ', '.join(current_expr)
        
        # Multilevel parsing strategy
        scalar_parsed = parse_scalar_tuple(tokens)
        final_expression = combine_expressions(scalar_parsed)
        
        return f'({final_expression})'
    
    def preprocess(self, expression):
        """
        Main preprocessing method
        
        Orchestrates the entire parsing and transformation process
        """
        try:
            # Step 1: Tokenization
            tokens = self.tokenize(expression)
            
            # Step 2: Expression Parsing
            processed_expression = self.parse_tuple_expression(tokens)
            
            return processed_expression
        
        except Exception as e:
            # Robust error handling
            error_msg = f"Parsing failed: {str(e)}"
            self.parsing_context['error_log'].append(error_msg)
            raise ValueError(error_msg)

# Example usage demonstration
def preprocess_tuple_expression(expr):
    parser = TupleExpressionParser()
    return parser.preprocess(expr)