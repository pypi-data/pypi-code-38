from kivy.uix.spinner import Spinner


class Selector(Spinner):
    def __init__(self, enum_type, **kwds):
        self.enum_type = enum_type
        super().__init__(
            text=enum_type.__name__,
            values=[e.pretty_string() for e in enum_type],
            **kwds
        )
        on_enum = getattr(self, 'on_enum', None)
        if on_enum:
            self.bind(enum=on_enum)

    def bind(self, enum=None, **kwds):
        kwds and super().bind(**kwds)
        if enum:

            def text_callback(instance, text):
                return enum(self, self.enum_type.make(text))

            super().bind(text=text_callback)

    def set(self, e):
        self.text = self.enum_type.make(e).pretty_string()
