"""
Demonstrating a false-positive of E1101 that should be suppressed by
pylint_protobuf.
"""


class Magic(object):
    _FIELDS = [('abc', 123)]

    def __init__(self):
        for attr, value in self._FIELDS:
            setattr(self, attr, value)


M = Magic()
print(M.abc)
