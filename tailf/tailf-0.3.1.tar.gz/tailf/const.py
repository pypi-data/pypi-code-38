__all__ = ["Truncated"]


class TailEvent:
    __slots__ = "_name"

    def __init__(self, name):
        self._name = name

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self._name)

    def __str__(self):
        return repr(self)


Truncated = TailEvent("Truncated")
