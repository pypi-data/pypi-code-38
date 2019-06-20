#
# This example shows how to write a basic calculator with variables.
#

from lark import Lark
from lark import tree as lark_tree

statement_grammar = """
    ?start: expression

    ?expression: statement
        | "(" expression ")"
        | expression "&&" expression        -> AND
        | expression "||" expression        -> OR
        | "!" expression                    -> NOT
    
    ?statement: function
        | VARIABLE "==" VALUE               -> EQUALITY
        | VARIABLE "!=" VALUE               -> INEQUALITY
        | VARIABLE
        
    ?function: function_name "(" VARIABLE "," VALUE ")"
    
    function_name: "edge" | "force" | "unforce"
    
    VARIABLE: NAME
    VALUE: NUMBER

    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.WS_INLINE
    
    %ignore WS_INLINE
"""


parser = Lark(statement_grammar, parser='earley', ambiguity='explicit')

def test():

    statement = "LinkaOn == 1 || (robotR1ProgramNumber == 1 && robotR2ProgramNumber !=  2 && edge(shuttleAtXY, 1))"

    tree = parser.parse(statement)
    print(tree.pretty())

    lark_tree.pydot__tree_to_png(tree, "statement.png")


if __name__ == '__main__':
    test()
    # main()
