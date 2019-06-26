from collections import Mapping


class CodelistCode(Mapping):
    def __init__(self, data, extension_name=None):
        self.data = data
        self.extension_name = extension_name

    def __eq__(self, other):
        if isinstance(other, CodelistCode):
            return self.data == other.data and self.extension_name == other.extension_name
        return dict.__eq__(self.data, other)

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        if self.extension_name:
            return 'CodelistCode(data={}, extension_name={})'.format(repr(self.data), repr(self.extension_name))
        return 'CodelistCode(data={})'.format(repr(self.data))

    def pop(self, *args):
        return self.data.pop(*args)
