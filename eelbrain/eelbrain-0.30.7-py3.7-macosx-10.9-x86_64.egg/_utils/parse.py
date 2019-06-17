# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
import ast


FLOAT_PATTERN = "^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$"
POS_FLOAT_PATTERN = "^[+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$"
INT_PATTERN = "^-?\d+$"
# matches float as well as NaN:
FLOAT_NAN_PATTERN = "^([Nn][Aa][Nn]$)|([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)$"


def find_variables(expr):
    """Find the variables participating in an expressions

    Returns
    -------
    variables : tuple of str
        Variables occurring in expr.
    """
    try:
        st = ast.parse(expr)
    except SyntaxError as error:
        raise ValueError("Invalid expression: %r (%s)" % (expr, error))
    return {n.id for n in ast.walk(st) if isinstance(n, ast.Name)}
