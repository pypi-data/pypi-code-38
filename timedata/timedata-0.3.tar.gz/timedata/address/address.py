"""
An address identifies how to get or set a piece of data within a Python object,
called the "root", using attributes and indexing.

An address description is a string looking like:

::

    foo.bar[32][5][baz].bang()

which would mean

"given an object "root", the value ``root.foo.bar[32][5]['baz'].bang()``".

Addresses are divided into "segments".

A segment contained in brackets ``[]`` is an index (for a list) or a key (for
a dictionary) - otherwise, it's an attribute.

In the example above, the segments are ``foo``, ``bar``, ``[32]``, ``[5]``,
``[baz]`` and ``bang``; ``foo`` and ``bar`` are attributes.
``baz`` is a string index, and ``32`` and ``5`` are numeric indexes.

You can use an Address to either get or set values in the root object.

Any key that's entirely numeric is taken to be an integer index.  This is
convenient but prevents the creation of dictionaries like
``{1: 'x', '1': 'y'}`` which you probably didn't want to do anyway.
"""

import json
from . import generate, segment


def number(s):
    try:
        return json.loads(s)
    except Exception:
        return s.strip()


class Address:
    def __init__(self, desc=None):
        self.segments = self.assignment = ()
        if not desc:
            return

        name, *assignment = desc.split('=', 1)
        assignment = assignment and assignment[0].strip()

        name = name.strip()

        try:
            self.segments = list(generate.generate(name))
        except Exception:
            raise ValueError('%s is not a legal address' % desc)

        if not (self.segments and assignment):
            return

        if isinstance(self.segments[-1], segment.Call):
            raise ValueError('Cannot assign to a call operation')

        self.assignment = tuple(number(s) for s in assignment.split(','))

    def __bool__(self):
        return bool(self.segments)

    def __str__(self):
        name = ''.join(str(i) for i in self.segments)
        if not self.assignment:
            return name

        assignment = ', '.join(str(i) for i in self.assignment)
        return '%s = %s' % (name, assignment)

    @staticmethod
    def _get(root, address):
        for a in address:
            root = a.get(root)
        return root

    def get(self, root):
        return self._get(root, self.segments)

    def set(self, root, *values):
        *first, last = self.segments
        parent = self._get(root, first)
        last.set(parent, *(self.assignment + values))
