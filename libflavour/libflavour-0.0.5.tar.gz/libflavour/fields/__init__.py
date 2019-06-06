import attr
from strictyaml import Map, Optional, Str

from .scalar import BooleanField, IntegerField, StringField
from .service import DatabaseField


class FieldFactory:
    def __init__(self):
        self.widgets = {
            BooleanField.identifier: BooleanField,
            IntegerField.identifier: IntegerField,
            StringField.identifier: StringField,
            DatabaseField.identifier: DatabaseField,
        }

    def get_widgets(self):
        return self.widgets

    def load(self, data):
        ret = []
        if "form" in data:
            for addon_name in data["form"]:
                widget_class = self.widgets[data["form"][addon_name]["type"]]
                widget = widget_class(name=addon_name, **data["form"][addon_name])
                ret.append(widget)
        return ret
