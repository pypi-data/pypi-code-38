"""
This submodule implements an OO abstraction for the query language.

Example:

cond('packageName', 'com.whatsapp') & cond('origin', 'GooglePlay')
=> "packageName:com.whatsapp AND origin:GooglePlay"
"""

from functools import reduce

class query:
    """
    Common interface for indentifing an OO query during typechecking.
    """
    def __or__(self, other):
        return _or(self, other)
        
    def __and__(self, other):
        return _and(self, other)

    def __neg__(self):
        return _not(self)

class query_group(query):
    def __init__(self, elems, join_op):
        self.elems = elems
        self.join_op = join_op

    def __str__(self):
        def f(e):
            if e is query_group:
                return "(%s)" % str(e)
            else:
                return str(e)
        return " {} ".format(self.join_op).join(map(f, self.elems))

class _or(query_group):
    """
    Represents an OR combination between elements in a query.
    """
    def __init__(self, left, right):
        if isinstance(left, list):
            if len(left) > 2:
                left = left[0] | left[1:]
            else:
                left = left[0] | left[1]
        if isinstance(right, list):
            if len(right) > 2:
                right = right[0] | right[1:]
            else:
                right = right[0] | right[1]
        super().__init__([left, right], 'OR')                

class _and(query_group):
    """
    Represents an AND combination between elements in a query.
    """
    def __init__(self, left, right):
        if isinstance(left, list):
            if len(left) > 2:
                left = left[0] & left[1:]
            else:
                left = left[0] & left[1]
        if isinstance(right, list):
            if len(right) > 2:
                right = right[0] & right[1:]
            else:
                right = right[0] & right[1]
        super().__init__([left, right], 'AND')

class _not(query):
    """
    Represents a negative query.
    """
    def __init__(self, inner):
        self.inner = inner

    def __neg__(self):
        return self.inner

    def __str__(self):
        return "-{}".format(self.inner)

class cond(query):
    """
    Represents a cond inside the query.
    If you want to create a fixed filter you should inherit from this class.
    """
    def __init__(self, field, condition, literal=False):
        self.field = field
        self.condition = condition
        self.literal = literal

    def __str__(self):
        if self.literal:
            fmt = "{field}:\"{condition}\""
        else:
            fmt = "{field}:{condition}"
        return fmt.format(field=self.field, condition=self.condition)

class packageName(cond):
    """
    Filter for package names of applications
    """
    def __init__(self, pkgName, literal=False):
        super().__init__('packageName', pkgName, literal)

fromGooglePlay = cond('origin', 'GooglePlay')
fromAppStore = cond('origin', 'AppleStore')

def or_many(*lst):
    return reduce(lambda x, y: x | y, lst)

def and_many(*lst):
    return reduce(lambda x, y: x & y, lst)
