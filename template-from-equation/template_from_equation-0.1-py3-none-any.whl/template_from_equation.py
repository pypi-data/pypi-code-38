import ast


BINOP_SYMBOLS = {
    ast.Add: "+",
    ast.Sub: "-",
    ast.Mult: "*",
    ast.Div: "/"
}


class Equation:
    '''The class for equation manipulation and making template from the associated equation
    
    To make template from equation, we use the ast trees. 
    When traversing an AST tree, it returns "n0, n1, n2, ..." for the leaf nodes of numbers, and "x0, x1, x2" for variables. 
    Then, an equation of "2+5*x" can be turned into its template "n0+n1*x0".
    (Using AST tree can help us avoid some subtle string matching difficulties of regular expression.)
    
    In some situations, we want to keep some constants in the equation unchanged.
    For example, to get the template of the equation "2+7*60 = x"  for the problem "How many minutes is 2 hours and 7 minutes?",
    we want to keep the constant "60" unchanged.
    In this situation, our function allows passing a number slot which contains only the numbers we want to substitute for our template. 
    (See the Example Usage below)
        
    Attributes:
        lhs: The left hand side of the equation storing in the format of an ast tree.
        rhs: The right hand side of the equation storing in the format of an ast tree.
    
    Example Usage:
        >>> eq1 = Equation("2+5")
        >>> eq1
        2 + 5
        >>> eq1.get_template()
        'n0 + n1'
        
        >>> eq2 = Equation("2+7*60 = x")
        >>> eq2
        2 + 7 * 60 = x
        >>> eq2.get_template()
        'n0 + n1 * n2 = x0'
        >>> eq2.get_template(num_slot=[2,7])
        'n0 + n1 * 60 = x0'
        
        >>> eq3 = Equation("2*x+5*12 = y")
        >>> eq3.get_template()
        'n0 * x0 + n1 * n2 = x1'
        >>> eq3.get_template(num_slot=[2,5])
        'n0 * x0 + n1 * 12 = x1'
        
    Reference:
        + [codegen: Some of the naming styles but not the code are adapted from codegen, which is a library to convert ast tree to python code] 
            (https://github.com/andreif/codegen) 
        
    '''
    
    def __init__(self, equation_string):
        '''
        Args:
            equation_string: A string of the equation we intend to manipulate.
        '''
        self.lhs = None
        self.rhs = None
        self._preprocess_equation_string(equation_string)
    
    
    def _preprocess_equation_string(self, equation_string):
        '''Convert the eqution input (a string) to the internal data format (ast tree)'''
        
        num_equal_sign = equation_string.count("=")

        if num_equal_sign == 0: 
            # If there is no equation sign and only an mathematical expression available
            self.lhs = ast.parse(equation_string, mode="eval")            
        elif num_equal_sign == 1:
            lhs_eq, rhs_eq = equation_string.split("=", 1)
            lhs_eq, rhs_eq = lhs_eq.lstrip().rstrip(), rhs_eq.lstrip().rstrip()
            self.lhs = ast.parse(lhs_eq, mode="eval")
            self.rhs = ast.parse(rhs_eq, mode="eval")
        else:
            raise("Invalid equation string input!")

    
    def __str__(self):

        def get_nodes_repr(node):
            '''Get the representation of the nodes in the equation tree recursively'''
            if isinstance(node, ast.BinOp): # 1. Get left 2. Get op 3. Get right
                nodes_repr = []
                nodes_repr.extend(get_nodes_repr(node.left))
                op_symbol = BINOP_SYMBOLS[type(node.op)]
                nodes_repr.append(op_symbol)
                nodes_repr.extend(get_nodes_repr(node.right))
                return nodes_repr
            elif isinstance(node, ast.Num):
                return [ str(node.n) ]
            elif isinstance(node, ast.Name):
                return [ str(node.id) ]

        if self.rhs:
            lhs = get_nodes_repr(self.lhs.body)
            rhs = get_nodes_repr(self.rhs.body)
            return " ".join(lhs) + " = " + " ".join(rhs)
        else:
            lhs = get_nodes_repr(self.lhs.body)
            return " ".join(lhs)

    
    def __repr__(self):
        return self.__str__()
    
    
    def get_template(self, num_slot=None):
        '''Get the equation template from equation
        
        This function makes the equation template by substituting the numbers in the number slot with "n0, n1, n2 ...",
        and variables with "x0, x1, x2, ....". 
        For example, 2 *x + 5 * y = z --> n1 * x1 + n2 * x2 = x3
        Further, we can replace only the numbers we pick by passing them through the list parameter "num_slot".
        
        Args:
            num_slot: A list which contains only the numbers we want to substitute for our template.
        '''
        
        counter_number = 0
        counter_variable = 0
        
        # If there is no number slot, collect all the numbers in the equation into the number slot
        if num_slot is None:
            num_slot = []
            for node in ast.walk(self.lhs):
                if isinstance(node, ast.Num):
                    num_slot.append(node.n)
            if self.rhs:
                for node in ast.walk(self.rhs):
                    if isinstance(node, ast.Num):
                        num_slot.append(node.n)

        def get_nodes_repr_template(node):
            '''Returns 'n0, n1, n2' for leaf nodes of numbers in the number slot and 'x0, x1, x2, ...' for leaf nodes of variables'''
            nonlocal counter_number
            nonlocal counter_variable
            if isinstance(node, ast.BinOp): # 1. Get left 2. Get op 3. Get right
                nodes_repr = []
                nodes_repr.extend(get_nodes_repr_template(node.left))
                op_symbol = BINOP_SYMBOLS[type(node.op)]
                nodes_repr.append(op_symbol)
                nodes_repr.extend(get_nodes_repr_template(node.right))
                return nodes_repr
            elif isinstance(node, ast.Num):
                if node.n in num_slot:
                    node_repr = "n{}".format(counter_number)
                    counter_number += 1
                    return [node_repr]
                else:
                    return [str(node.n)]
            elif isinstance(node, ast.Name):
                node_repr = "x{}".format(counter_variable)
                counter_variable += 1
                return [node_repr]

        if self.rhs:
            lhs = get_nodes_repr_template(self.lhs.body)
            rhs = get_nodes_repr_template(self.rhs.body)
            return " ".join(lhs) + " = " + " ".join(rhs)
        else:
            lhs = get_nodes_repr_template(self.lhs.body)
            return " ".join(lhs)