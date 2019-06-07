import json

def print_help(parameters_list):

    print("\nParameters: ")

    for p in parameters_list:
        print('\n')
        if 'description' in p:
            print(p['name'], end=': ')
            print(p['description'], end='. ')
        else:
            print(p['name'], end='. ')
            print("no descrption", end='. ')

        if len(p['allowed_values']) == 0:
            pass
            #print("Allowed values: any", end=". ")
        else:
            print("Allowed values: " + str(p['allowed_values']), end=". ")

        if p['requires_value'] == True:
            print("Required.")
        else:
            print("Optional.")

    print("\n")

    print("Note: args must be indicated with a one or two leading dashes. \nExample: ./script_name --parameter1 value1 value2 -parameter2 value3\n")

def arg_parser(argv, parameters):

    arg_d = {}

    current_arg = None

    for idx, arg in enumerate(argv):

        if "help" in arg.lower():
            print_help(parameters)
            quit()


        if arg[0] == '-':
            current_arg = arg

            arg_d[arg] = []
        else:
            #value
            if current_arg == None:
                pass

            else:
                arg_d[current_arg].append(arg)

    return arg_d


if __name__ == '__main__':
    # # TEST # #

    mocKv = ['ex1.py', '--bucket', 'fucet', 'ASDF', '--action', 'delete']

    arg_parser(mocKv)
