"""
Provide common functions to the other modules in pikachu

Methods:
syntax_error -- print information about syntax errors in the pikachu program
"""

from click import secho


def pika_error(line_num, msg):
    """
    Display information about syntax errors in the pikachu program then exit.

    Arguments:
    lineNo -- the line where the syntax error was found.
    """
    pika_print('SyntaxError in line {}: {}'.format(line_num, msg))
    exit()


def pika_print(msg, nl=False, fg='yellow'):
    if type(msg) != str:
        msg = str(msg)
    secho(msg, fg=fg, nl=nl)
