"""
Module for safely evaluating arithmetic expressions in strings.

http://stackoverflow.com/a/9558001
"""

import ast
import operator as op

# supported operators
operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
             ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
             ast.USub: op.neg}


def eval_expr(expr, variables=None):
    """
    Safely evaluates a simple mathematical expression passed as a string.

    Parameters
    ----------
    expr : str
        The expression to evaluate.
    variables : dict, optional
        Dict mapping variable names to values. These variables can then be used
        as substrings of ``expr``. Pass None to evaluate the expression without
        using any named variables.

    Returns
    -------
    numeric
        The result of evaluating the expression.

    Examples
    --------
    >>> eval_expr('2^6')
    4
    >>> eval_expr('2**6')
    64
    >>> eval_expr('1 + 2*3**(4^5) / (6 + -7)')
    -5.0
    """
    if variables is None:
        variables = {}
    return eval_(ast.parse(expr, mode='eval').body, variables)


def eval_(node, variables):
    """
    Inner function for safely evaluating a particular node of an abstract syntax
    tree. Called recursively to evaluate a string as part of ``eval_expr()``.

    Parameters
    ----------
    node : ast.AST
        The node of the abstract syntax tree to evaluate.
    variables : dict
        Dictionary of named variables to use during evaluation.

    Returns
    -------
    numeric
        The result of evaluating the node.
    """
    if isinstance(node, ast.Num):  # <number>
        return node.n
    elif isinstance(node, ast.BinOp):  # <left> <operator> <right>
        return operators[type(node.op)](eval_(node.left, variables),
                                        eval_(node.right, variables))
    elif isinstance(node, ast.UnaryOp):  # <operator> <operand> e.g., -1
        return operators[type(node.op)](eval_(node.operand, variables))
    elif isinstance(node, ast.Name):
        return variables[node.id]
    else:
        raise TypeError(node)
