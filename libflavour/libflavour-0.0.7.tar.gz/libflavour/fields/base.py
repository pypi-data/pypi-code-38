import attr
from strictyaml import Bool, Int, Map, Optional, Str


@attr.s
class BaseField:
    name = attr.ib()  # System name
    type = attr.ib()  # The type/identifier of the widget
    label = attr.ib()
    helptext = attr.ib(default="")
    default = attr.ib(default=None)
    visibility = attr.ib(default=0)
    required = attr.ib(default=True)
    readonly = attr.ib(default=False)

    @classmethod
    def schema(cls):
        basic_schema = {
            "label": Str(),
            "type": Str(),
            Optional("helptext"): Str(),
            Optional("visibility"): Int(),
            Optional("required"): Bool(),
            Optional("readonly"): Bool(),
        }

        return Map({**basic_schema, **cls.additional_schema()})

    @classmethod
    def additional_schema(cls):
        """
        At least the `default` value must be set here.
        return {
            "default": Str(),
        }

        """
        raise NotImplemented

    @property
    def data(self):
        basic_data = {
            "name": self.name,
            "type": self.type,
            "label": self.label,
            "helptext": self.helptext,
            "default": self.default,
            "visibility": self.visibility,
            "required": self.required,
            "readonly": self.readonly,
        }
        return {**basic_data, **self.additional_data()}

    def additional_data(self):
        return {}

    def transform(self, data):
        return data
