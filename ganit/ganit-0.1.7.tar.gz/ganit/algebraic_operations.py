from math import *
from .utils import *
from .handle_invalid_scenarios import handle_invalid_scenario


def roundOp(arg):
    if is_int(arg[0]):
        return round(arg[1], int(arg[0]))
    else:
        handle_invalid_scenario("Rounding takes only 'int' as second argument")


def fact(arg):
    if is_int(arg[0]) == False or int(arg[0]) < 0:
        handle_invalid_scenario(
            "Value Error: " + format(arg[0]) +
            ". Factorial calculation can only be done for integers greater than 0."
        )
    return (factorial(arg[0]))


def gcdOp(arg):
    if (is_int(arg[0]) == False) or (is_int(arg[1]) == False):
        handle_invalid_scenario("Value Error: " + format(arg[0]) + " , " +
                                format(arg[1]) +
                                ". GCD can only be determined for integers.")
    return gcd(int(arg[1]), int(arg[0]))


def square(arg):
    if arg[0] < 0:
        handle_invalid_scenario("Square root only works for positive numbers")
    return sqrt(arg[0])


algebraic = {
    "abs": lambda arg: abs(arg[0]),
    "ceil": lambda arg: ceil(arg[0]),
    "floor": lambda arg: floor(arg[0]),
    "round": lambda arg: roundOp(arg),
    "factorial": lambda arg: fact(arg),
    "gcd": lambda arg: gcdOp(arg),
    "exp": lambda arg: exp(arg[0]),
    "pow": lambda arg: pow(arg[1], arg[0]),
    "sqrt": lambda arg: square(arg),
    "log": lambda arg: log10(arg[0]),
    "ln": lambda arg: log(arg[0]),
    "log2": lambda arg: log2(arg[0]),
    "Log": lambda arg: log(arg[1], arg[0])
}
