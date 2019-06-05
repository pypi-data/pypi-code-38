import json

def arg_parser(argv):

    arg_d = {}

    current_arg = None

    for idx, arg in enumerate(argv):
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
