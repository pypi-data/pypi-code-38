from marshmallow import Schema as MSchema
from schema import And, Use


class Value(And):
    def __init__(self, *args, **kwargs):
        self.optional = kwargs.get('optional', False)
        if 'optional' in kwargs.keys():
            del kwargs['optional']
        self.original_types = args
        self.types = args
        self.kwargs = kwargs
        self.refresh()

    def refresh(self):
        n = []
        for a in self.types:
            if a == int:
                a = Use(int)
            n.append(a)
        And.__init__(self, *n, **self.kwargs)


class NestedValue:
    def __init__(self, response_class, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.nested_class = response_class
