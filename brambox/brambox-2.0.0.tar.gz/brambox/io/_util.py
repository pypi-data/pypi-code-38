#
#   Copyright EAVISE
#   Author: Maarten Vandersteegen
#   Author: Tanguy Ophoff
#
import os
from pathlib import Path
import glob

__all__ = ["expand"]


def files(folder):
    """ List all files in a directory omitting directories. """
    for filepath in Path(folder).glob('*'):
        if filepath.is_file():
            yield str(filepath)


def strider(elements, stride, offset):
    """ Yield input elements with given stride and offset. """
    next_element = offset

    for i, elem in enumerate(elements):
        if i == next_element:
            next_element += stride
            yield elem


def modulo_expand(expr, stride, offset):
    """ Expands a path with a **%d** to files with different numbers. """
    number = offset

    while True:
        filename = expr % number
        if not os.path.isfile(filename):
            break
        yield filename
        number += stride


def expand(expr, stride=1, offset=0):
    """ Expand a file selection expression into multiple filenames.

    Args:
        expr (str): File sequence expression
        stride (int, optional): Sample every n'th file where n is this parameter; Default **1**
        offset (int, optional): Start with the m'th file where m is this parameter; Default **0**

    Returns:
        generator: Iterable object that produces full filenames

    Note:
        The ``expr`` parameter can be one of the following expressions:

        - a file itself -> return filename
        - a directory -> return files from directory and subdirectories (recursive)
        - path with **'*'** wildcard -> return globbed files (recursive if **'\\*\\*'** is used)
        - path with **'%d'** wildcard -> return incremental files

    Warning:
        If you use **'\\*'** wildcards in your expression, this function glob it recursively,
        meaning **'\\*\\*'** wildcards will go down through all the subdirectories.
        If the folder contains symlinked loops, this will cause this function to generate the same files over and over again.
    """
    if stride <= 0:
        raise ValueError('Stride must be a strictly positive integer')
    if offset < 0:
        raise ValueError('Offset must be a positive integer')

    if os.path.isdir(expr):
        return strider(sorted(files(expr)), stride, offset)
    elif os.path.isfile(expr):
        return [expr]
    elif '*' in expr:
        return strider(sorted(glob.glob(expr, recursive=True)), stride, offset)
    elif '%' in expr:
        return modulo_expand(expr, stride, offset)
    else:
        raise TypeError("File selection expression invalid")
