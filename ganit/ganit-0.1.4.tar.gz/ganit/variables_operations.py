from math import *
from .utils import *
from .handle_invalid_scenarios import handle_invalid_scenario
default_variables = {
    "pi": pi,
    "e": e,
    "tau": 2 * pi,
    "True": True,
    "False": False
}


def perform_operation(operator, arg):

    if operator == '+':
        return arg[1] + arg[0]
    elif operator == '-':
        return arg[1] - arg[0]
    elif operator == '*':
        return arg[1] * arg[0]
    elif operator == '/':
        return arg[1] / arg[0]
    elif operator == '%':
        return arg[1] % arg[0]
    elif operator == '^':
        return arg[1]**arg[0]
    elif operator == 'abs':
        return abs(arg[0])
    elif operator == 'ceil':
        return ceil(arg[0])
    elif operator == 'floor':
        return floor(arg[0])
    elif operator == 'round':
        if is_int(arg[0]):
            return round(arg[1], int(arg[0]))
        else:
            handle_invalid_scenario("Rounding takes only 'int' as second argument")
    elif operator == 'factorial':
        if is_int(arg[0]) == False or int(arg[0]) < 0:
            handle_invalid_scenario(
                "Value Error: " + format(arg[0]) +
                ". Factorial calculation can only be done for integers greater than 0.")
        return factorial(int(arg[0]))
    elif operator == 'gcd':
        if (is_int(arg[0]) == False) or (is_int(arg[1]) == False):
            handle_invalid_scenario(
                "Value Error: " + format(arg[0]) + " , " + format(arg[1]) +
                ". GCD can only be determined for integers.")
        return gcd(int(arg[1]), int(arg[0]))
    elif operator == 'exp':
        return exp(arg[0])
    elif operator == 'pow':
        return pow(arg[1], arg[0])
    elif operator == 'sqrt':
        if arg[0] < 0:
            handle_invalid_scenario("Square root only works for positive numbers")
        return sqrt(arg[0])
    elif operator == 'log':
        return log10(arg[0])
    elif operator == 'ln':
        return log(arg[0])
    elif operator == 'log2':
        return log2(arg[0])
    elif operator == 'Log':
        return log(arg[1], arg[0])
    elif operator == 'sin':
        return sin(arg[0])
    elif operator == 'cos':
        return cos(arg[0])
    elif operator == 'tan':
        return tan(arg[0])
    elif operator == 'asin':
        return asin(arg[0])
    elif operator == 'acos':
        return acos(arg[0])
    elif operator == 'atan':
        return atan(arg[0])
    elif operator == 'sinh':
        return sinh(arg[0])
    elif operator == 'cosh':
        return cosh(arg[0])
    elif operator == 'tanh':
        return tanh(arg[0])
    elif operator == 'asinh':
        return asinh(arg[0])
    elif operator == 'acosh':
        return acosh(arg[0])
    elif operator == 'atanh':
        return atanh(arg[0])
    elif operator == 'hypot':
        return hypot(arg[1], arg[0])
    elif operator == 'deg':
        return degrees(arg[0])
    elif operator == 'rad':
        return radians(arg[0])
    elif operator == '?':
        if isinstance(arg[1], bool) and arg[1] == True:
            return arg[0]
        elif isinstance(arg[1], bool) and arg[1] == False:
            return arg[1]
        else:
            handle_invalid_scenario("'?:' only works for boolean condition")
    elif operator == ":":
        if isinstance(arg[1], bool) and arg[1] == False:
            return arg[0]
        else:
            return arg[1]
    elif operator == ">":
        return arg[1] > arg[0]
    elif operator == "<":
        return arg[1] < arg[0]
    elif operator == "=":
        return arg[1] == arg[0]
    elif operator == "@":
        return arg[1] >= arg[0]
    elif operator == "#":
        return arg[1] <= arg[0]
    elif operator == '!':
        return arg[0] != arg[1]
    elif operator == '~':
        if not is_bool(arg[0]):
            handle_invalid_scenario("'!' only works for boolean")
        return not arg[0]
    elif operator == '|':
        if isinstance(arg[1], bool) and isinstance(arg[0], bool):
            return arg[0] or arg[1]
        else:
            handle_invalid_scenario("'|' only works for boolean conditions")
    elif operator == '&':
        if isinstance(arg[1], bool) and isinstance(arg[0], bool):
            return arg[0] and arg[1]
        else:
            handle_invalid_scenario("'&' only works for boolean conditions")
