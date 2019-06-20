from rook.exceptions import RookWriteAttributeNotSupported, RookAttributeNotFound, RookMethodNotFound


class Namespace(object):
    def __init__(self, methods=None):
        self._methods = {}

        if methods:
            for method in methods:
                self._methods[method.__name__] = method

    def call_method(self, name, args):
        try:
            method = self._methods[name]
        except KeyError:
            raise RookMethodNotFound(type(self), name)

        return method(self, args)

    def read_attribute(self, name):
        try:
            return getattr(self, name)
        except AttributeError:
            raise RookAttributeNotFound(name)

    def write_attribute(self, name, value):
        raise RookWriteAttributeNotSupported(type(self), name)

    def read_key(self, key):
        try:
            return self[key]
        except KeyError:
            raise RookAttributeNotFound(key)

    def to_dict(self):
        raise NotImplementedError()

    def to_simple_dict(self):
        raise NotImplementedError()
