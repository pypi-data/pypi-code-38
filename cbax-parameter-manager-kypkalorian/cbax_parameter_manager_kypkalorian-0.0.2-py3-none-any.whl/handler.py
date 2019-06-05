import sys

from .arg_build              import arg_build
from .arg_parser             import arg_parser
from .validate_parameters    import validate_parameters

def handler_func(args, mainFunction, parameters):

    arg_d = arg_parser(args)

    if not (validate_parameters(arg_d, parameters)):
        print("parameter validation failed")
        return

    mainFunction(arg_d)
