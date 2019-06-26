from inspect import getmembers, getsourcelines

PAD_LEFT = 0
PAD_RIGHT = 1

class Field():
    def __init__(self, size=0, sep=' ',pad=PAD_LEFT, nofp=True):
        self._size = size
        self._sep = sep
        self._value = None
        self._pad = pad
        self._nofp = nofp

    def __set__(self, instance, value):
        self._value = value


class Base():
    _fields = {}

    def __init__(self):
        allfields = list(type(self).__dict__)

        for name, attribute in getmembers(self, lambda o: isinstance(o, Field)):
            sortkey = allfields.index(name)

            attribute._sortkey = sortkey
            attribute._fieldname = name
            self._fields[name] = attribute


    def __repr__(self):
        line = []

        for _, val in sorted(self._fields.items(),key=lambda o: o[1]._sortkey):
            value = val._value

            if val._nofp and type(value) == float:
                value = str(round(value, 2)).replace(".","")

            if val._pad == PAD_RIGHT:
                column = str(value).rjust(val._size, val._sep)
            else:
                column = str(value).ljust(val._size, val._sep)

            line.append(column[:val._size])

        return ''.join(line)