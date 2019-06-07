import sys

from .arg_parser             import arg_parser
from .validate_parameters    import validate_parameters

def parameter_manager(args, mainFunction, parameters):

    arg_d = arg_parser(args, parameters)

    if not (validate_parameters(arg_d, parameters)):
        #Failure message for all
        print("Note: args must be indicated with a one or two leading dashes. \nExample: ./script_name --parameter1 value1 value2 -parameter2 value3\n")
        print("pass in \"help\" for assistance")
        return
    else:
        pass
        #parameters validated

    arg_new = {}

    for item in arg_d:
        arg_new[item.replace("-", "")] = arg_d[item]

    mainFunction(arg_new)
