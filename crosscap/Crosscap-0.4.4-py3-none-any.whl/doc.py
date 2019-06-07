"""
Extracting documentation from python objects
"""
import inspect
import re

from builtins import object

import attr

import ftfy


@attr.s
class Documentation(object):
    """
    A docstring parser
    """
    raw = attr.ib()
    decode = attr.ib(default=False)

    @property
    def first(self):
        return self.raw.split('\n')[0]

    @property
    def full(self):
        """
        The full docstring, line-folded
        """
        # conveniently, all these calls return unicode if they're passed in unicode, so we
        # won't mangle unicode docstrings at this point.
        out = re.sub(r'\n\n', '\v', self.raw)
        return out.replace('\n', ' ').replace('\v', '\n\n')

    @classmethod
    def fromObject(cls, obj, decode=None):
        """
        Construct a `Documentation` from any object with a docstring

        With `decode=True`, decode docstrings as utf-8, then run them through ftfy, and return unicode.
        This is for compatibility with Python 2, where docstrings are usually byte strings.
        """
        if obj.__doc__ is None:
            return cls(u'' if decode else '')
        r = cls.fromString(obj.__doc__, decode=decode)
        return r

    @classmethod
    def fromString(cls, s, decode=None):
        out = inspect.cleandoc(s)
        if decode and isinstance(out, bytes): # pragma: nocover (doesn't run in python 3)
            return cls(ftfy.fix_encoding(out.decode('utf-8')))
        else:
            return cls(out)


def doc(obj):
    """
    The most common case, just give me the first line
    """
    return Documentation.fromObject(obj).first
