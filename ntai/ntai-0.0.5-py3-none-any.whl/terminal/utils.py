import inspect, sys

def variable_name(variable):
    '''
    Argument:
        variable: the variable to search for from outer-most frame inner-wards

    Returns:
        name (str): the string characters corresponding to the name of the
            variable
    '''
    for fi in reversed(inspect.stack()):
        names = [
            var_name
            for var_name, var_val in fi.frame.f_locals.items()
            if var_val is variable
        ]
        if len(names) > 0:
            return names[0]


def error_message(command, error='', stdout_data=None, stderr_data=None):
    '''
    Arguments:
        command (list): a list of strings indiciating the command and its
            arguments

        error (Error): Optional. By default ''. The error thrown.

        stdout_data: Optional. By default None. If provided, writes to
            sys.stderr.

        stderr_data: Optional. By default None. If provided, writes to
            sys.stderr.

    Returns:
        None
    '''

    msg = '\nERROR during execution of {cmd}:\t{err}\n'.format(cmd=' '.join(command), err=str(error))
    print(msg, file=sys.stderr)
    if stdout_data is not None:
        print("\nStandard output:\n----------------", file=sys.stderr)
        print(stdout_data, file=sys.stderr)
    if stderr_data is not None:
        print("\nStandard output:\n----------------", file=sys.stderr)
        print(stderr_data, file=sys.stderr)
    return
