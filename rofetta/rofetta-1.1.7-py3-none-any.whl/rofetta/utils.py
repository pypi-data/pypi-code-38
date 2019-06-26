
import os
import tempfile
from functools import wraps


def format_from_filename(fname:str) -> str or None:
    """Return the format associated with given filename"""
    return os.path.splitext(fname)[1][1:]
def basename_from_filename(fname:str) -> str or None:
    """Return the format associated with given filename"""
    return os.path.splitext(fname)[0]


def output_as_tempfile(func):
    """Make conversion functions working with only input file, and returning
    their output (temp)file.

    """
    @wraps(func)
    def wrapper(fin, fout=None):
        if not fout:
            with tempfile.NamedTemporaryFile('w', delete=False) as fd:
                fout = fd.name
        func(fin, fout)
        return fout
    return wrapper


def as_asp_value(value:str) -> str:
    """Return given value ready to be integrated into ASP data.

    >>> as_asp_value('ab')
    'ab'
    >>> as_asp_value('a,b')
    '"a,b"'
    >>> as_asp_value('a b')
    '"a b"'
    >>> as_asp_value('0')
    '0'
    >>> as_asp_value('0a')
    '"0a"'
    >>> as_asp_value('aɨb')
    '"aɨb"'

    """

    correct_asp = value.isnumeric() or (value.isidentifier() and value[0].islower())
    utf8 = any(ord(c) > ord('z') for c in value)
    if correct_asp and not utf8:
        return value
    return '"' + value + '"'
