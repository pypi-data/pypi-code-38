"""
This module contains classes to use in tests when defining instances for
monoid, functor, etc.
"""


class Wrapper:
    """Wrap a single value"""

    def __init__(self, val):
        self.val = val

    def __repr__(self):
        return "Wrapper({})".format(self.val)

    def __eq__(self, other):
        return isinstance(other, Wrapper) and self.val == other.val


class Sequence:
    """Container for multiple items.  Isomorphic to a tuple."""

    def __init__(self, *items):
        self.items = items

    def __repr__(self):
        return "Sequence({})".format(', '.join(map(repr, self.items)))

    def __eq__(self, other):
        return isinstance(other, Sequence) and self.items == other.items


class Pair:
    """Contains a pair of two items.  Isomorphic to a 2-tuple."""

    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __repr__(self):
        return "Pair({}, {})".format(repr(self.a), repr(self.b))

    def __eq__(self, other):
        return self.a == other.a and self.b == other.b
