from types import FunctionType

"""
Show data from some objects, methods, properties, etc

"""

def methods(cls):
    return [x for x, y in cls.__dict__.items() if type(y) == FunctionType]

def methods_dict(cls):
    methods = dict()
    {methods.update({x: y}) for x, y in cls.__dict__.items()
     if type(y) == FunctionType}
    return methods
