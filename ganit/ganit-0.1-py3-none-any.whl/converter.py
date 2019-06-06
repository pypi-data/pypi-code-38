# A python utility to evaluate an Infix expression.
from .utils import *
from .variables_operations import default_variables
from .all_operators import all_operators
from .handle_invalid_scenarios import *
def convert(exp, variables):
    if is_float(exp) or is_int(exp):
        return exp
    if variables is not None:
        variables = {**default_variables, **variables}
    else:
        variables = default_variables
    operands = []
    stack = []
    operand = ""
    postFix = ""
    stack.append('(')

    def add_operand():
        nonlocal postFix, operand
        operand = operand.strip()
        if is_valid_operand(operand, variables):
            operands.append(operand)
            postFix += operand + " "
            return True
        else:
            return False

    def add_operator(operator):
        nonlocal stack, postFix
        if operator in all_operators:
            if operator == '(':
                stack.append(operator)
            elif operator == ')':
                stackOperator = stack.pop()
                while stackOperator != '(':
                    postFix += stackOperator + " "
                    stackOperator = stack.pop()
            else:
                operatorPrecedence = all_operators[operator]["precedence"]
                stackOperator = stack.pop()
                while all_operators[stackOperator]["precedence"] >= operatorPrecedence:
                    postFix += stackOperator + " "
                    stackOperator = stack.pop()
                stack.append(stackOperator)
                stack.append(operator)
            return True
        else:
            return False

    if len(exp) == 0:
        handle_invalid_scenario("Invalid Expression: " + exp)

    if len(exp) > 0 and exp[-1] in all_operators and exp[-1] != ')':
        handle_invalid_scenario(
            "Expression ends with an operator, which is invalid. System will exit"
        )
    exp += ')'
    for letter in exp:
        if letter in all_operators:
            #Some operators can be more than one letter. So, checking if that is an operator
            check = add_operand() or add_operator(operand)
            if not check:
                handle_invalid_scenario("Invalid input " + operand)
            operand = ""
            add_operator(letter)
        else:
            operand += letter
    add_operand()
    postFix= postFix.replace(",", "")
    postFix= postFix.replace("  ", " ")
    return postFix
