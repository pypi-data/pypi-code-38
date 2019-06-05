import sys

from .arg_parser             import arg_parser
from .validate_parameters    import validate_parameters

def parameter_manager(args, mainFunction, parameters):

    arg_d = arg_parser(args)

    if not (validate_parameters(arg_d, parameters)):
        print("parameter validation failed")
        return

    mainFunction(arg_d)
