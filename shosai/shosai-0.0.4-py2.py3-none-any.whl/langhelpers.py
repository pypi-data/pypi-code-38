import os.path
from collections import defaultdict


class reify(object):
    """cached property"""

    def __init__(self, wrapped):
        self.wrapped = wrapped
        try:
            self.__doc__ = wrapped.__doc__
        except Exception:
            pass

    def __get__(self, inst, objtype=None):
        if inst is None:
            return self
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val


def normalize_linesep_text(text):
    lines = [line for line in text.rstrip().splitlines()]
    lines.append("")
    return os.linesep.join(lines)


class NameStore:
    """
    >>> one = object()
    >>> two = object()
    >>> store = NameStore()
    >>> store[one] = "foo"
    >>> store[two] = "foo"
    >>> store[one]
    "foo"
    >>> store[two]
    "foo01"
    """

    def __init__(self):
        self.c = defaultdict(int)
        self.value_to_uid_mapping = {}
        self.uid_to_value_mapping = {}

    def __contains__(self, value):
        return value in self.value_to_uid_mapping

    def __setitem__(self, value, name):
        if value not in self.value_to_uid_mapping:
            uid = self.get_or_create_uid(value, name)
            self.value_to_uid_mapping[value] = uid
            self.c[name] += 1
            self.uid_to_value_mapping[uid] = value

    def __getitem__(self, value):
        return self.value_to_uid_mapping[value]

    def reverse_lookup(self, uid):
        return self.uid_to_value_mapping[uid]

    def get_or_create_uid(self, value, name):
        try:
            return self[value]
        except KeyError:
            i = self.c[name]
            return self._generate_uid(name, i)

    def _generate_uid(self, name, i):
        if i == 0:
            return name
        else:
            base, ext = os.path.splitext(name)
            if not ext:
                return "{}{:02d}".format(name, i)
            else:
                return "{}{:02d}{ext}".format(base, i, ext)
