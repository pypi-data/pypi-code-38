from .field import Field

class FormMeta(type):
    
    def __init__(cls, name, bases, namespace):
        fields = {}
        for key, value in namespace.items():
            if isinstance(value, Field):
                fields[key] = value
        cls.fields = fields
        super().__init__(name, bases, namespace)

class Form(metaclass=FormMeta):

    def __init__(self, t, data):
        self.t = t
        self.raw_data = data

    @property
    def raw_data(self):
        return self._raw_data

    @raw_data.setter
    def raw_data(self, data):
        self._raw_data = data or {}
        self.data = None
        self.errors = None

    def validate(self):
        data = {}
        errors = {}
        valid = True
        self.data = None

        for name, field in self.fields.items():
            value = self.raw_data.get(name)
            field_errors, value = field.validate(name, value, self)
            if field_errors:
                errors[name] = field_errors
                valid = False
            else:
                data[name] = value

        self.errors = errors
        if valid:
            self.data = data
        return valid
