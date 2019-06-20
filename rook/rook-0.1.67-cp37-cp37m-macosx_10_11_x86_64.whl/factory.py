
from rook.exceptions import RookUnknownObject


class Factory(object):

    def __init__(self):
        self.__methods = {}

    def get_object(self, name, *args, **kwargs):
        return self.get_object_factory(name)(*args, **kwargs)

    def get_object_factory(self, name):
        try:
            return self.__methods[name.lower()]
        except KeyError:
            raise RookUnknownObject(name)

    def register_method(self, method, name=None):
        if not name:
            if hasattr(method, 'NAME'):
                name = method.NAME
            else:
                name = method.__name__

        self.__methods[name.lower()] = method

    def register_methods(self, methods):
        for method in methods:
            self.register_method(method)

    def import_methods(self, methods):
        if isinstance(methods, (list, tuple)):
            self.register_methods(methods)
        else:
            self.__methods.update(methods)
