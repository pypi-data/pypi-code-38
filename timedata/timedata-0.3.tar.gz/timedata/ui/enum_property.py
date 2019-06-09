from kivy.properties import OptionProperty


class EnumProperty(OptionProperty):
    def __init__(self, default, **kwds):
        self.enum_type = default.__class__
        options = [str(e) for e in self.enum_type]
        super().__init__(default, options=options, **kwds)

    def __set__(self, obj, val):
        self.set(obj, str(val))

    def __get__(self, obj, objtype):
        if obj is None:
            return self
        return self.enum_type[self.get(obj)]
