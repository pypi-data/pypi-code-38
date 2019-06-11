from math import *

trigonometric = {
    "sin": lambda arg: sin(arg[0]),
    "cos": lambda arg: cos(arg[0]),
    "tan": lambda arg: tan(arg[0]),
    "asin": lambda arg: asin(arg[0]),
    "acos": lambda arg: acos(arg[0]),
    "atan": lambda arg: atan(arg[0]),
    "sinh": lambda arg: sinh(arg[0]),
    "cosh": lambda arg: cosh(arg[0]),
    "tanh": lambda arg: tanh(arg[0]),
    "asinh": lambda arg: asinh(arg[0]),
    "acosh": lambda arg: acosh(arg[0]),
    "atanh": lambda arg: atanh(arg[0]),
    "hypot": lambda arg: hypot(arg[1], arg[0]),
    "deg": lambda arg: degrees(arg[0]),
    "rad": lambda arg: radians(arg[0])
}