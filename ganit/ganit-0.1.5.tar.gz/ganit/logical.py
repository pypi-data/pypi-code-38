from math import *
from .utils import *
from .handle_invalid_scenarios import handle_invalid_scenario


def question(arg):
    if isinstance(arg[1], bool) and arg[1] == True:
        operated = True
        return arg[0]
    elif isinstance(arg[1], bool) and arg[1] == False:
        operated = True
        return arg[1]
    else:
        handle_invalid_scenario("'?:' only works for boolean condition")


def colon(arg):
    if isinstance(arg[1], bool) and arg[1] == False:
        return arg[0]
    else:
        return arg[1]


def inverse(arg):
    if not is_bool(arg[0]):
        handle_invalid_scenario("'!' only works for boolean")
    return not arg[0]


def orOp(arg):
    if isinstance(arg[1], bool) and isinstance(arg[0], bool):
        return arg[0] or arg[1]
    else:
        handle_invalid_scenario("'|' only works for boolean conditions")


def andOp(arg):
    if isinstance(arg[1], bool) and isinstance(arg[0], bool):
        return arg[0] and arg[1]
    else:
        handle_invalid_scenario("'&' only works for boolean conditions")


logical = {
    "?": lambda arg: question(arg),
    ":": lambda arg: colon(arg),
    ">": lambda arg: arg[1] > arg[0],
    "<": lambda arg: arg[1] < arg[0],
    "=": lambda arg: arg[1] == arg[0],
    "@": lambda arg: arg[1] >= arg[0],
    "#": lambda arg: arg[1] <= arg[0],
    "!": lambda arg: arg[1] != arg[0],
    "~": lambda arg: inverse(arg),
    '|': lambda arg: orOp(arg),
    '&': lambda arg: andOp(arg)
}