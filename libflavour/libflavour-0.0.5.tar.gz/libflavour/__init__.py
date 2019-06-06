__author__ = "Divio AG"
__email__ = "dennis.schwertel@divio.ch"
__version__ = "0.0.5"
__url__ = "https://www.divio.com"

import strictyaml

from .exceptions import ValidationException
from .fields import FieldFactory
from .schema import schema_addon, schema_project


def get_fields_schemas():
    widgets = FieldFactory().get_widgets()
    widget_schema = None
    for widget in widgets:
        if not widget_schema:
            widget_schema = widgets[widget].schema()
            continue
        widget_schema |= widgets[widget].schema()
    return widget_schema


def get_schema_for_type(type):
    widgets = FieldFactory().get_widgets()
    for widget in widgets:
        if widgets[widget].identifier == type:
            return widgets[widget].schema()


def load_addon(yaml_string):
    try:
        yaml_data = strictyaml.load(yaml_string, schema_addon)

        if "form" in yaml_data.data:
            for widget in yaml_data.data["form"]:
                yaml_data["form"][widget].revalidate(
                    get_schema_for_type(yaml_data.data["form"][widget]["type"])
                )

        ff = FieldFactory()
        return ff.load(yaml_data.data)

    except strictyaml.exceptions.YAMLValidationError:
        raise ValidationException


def load_project(yaml_string):
    try:
        yaml_data = strictyaml.load(yaml_string, schema_project)

        if "form" in yaml_data.data:
            for widget in yaml_data.data["form"]:
                yaml_data["form"][widget].revalidate(
                    get_schema_for_type(yaml_data.data["form"][widget]["type"])
                )

        ff = FieldFactory()
        return {
            "slug": yaml_data.data["slug"],
            "addons": yaml_data.data["addons"] if "addons" in yaml_data.data else [],
            "services": yaml_data.data["services"],
            "form": ff.load(yaml_data.data),
        }

    except strictyaml.exceptions.YAMLValidationError:
        raise ValidationException
