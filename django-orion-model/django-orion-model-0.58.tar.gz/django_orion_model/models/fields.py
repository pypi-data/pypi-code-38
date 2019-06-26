from django.contrib.postgres.fields import JSONField, ArrayField
from django.db import models
from logging import getLogger

logger = getLogger(__name__)


class OrionField:
    orion_field = True
    orion_type_mismatch_permissive = True
    valid_orion_types = ("Text", "String", "Number", "Boolean", "StructuredValue", "DateTime",
                         "geo:point", "geo:line", "geo:box", "geo:polygon", "geo:json")

    def extract_from_json(self, json_data):
        attribute = json_data.get(self.name)
        if attribute is None:
            raise KeyError(self.name + " Not included in data")
        if attribute["type"] not in self.valid_orion_types:
            message = "Django orion field {0} received type {1} is not valid options: {2}".format(
                            self.name, attribute["type"], ",".join(self.valid_orion_types))
            if self.orion_type_mismatch_permissive:
                logger.debug(message)
            else:
                raise Exception(message)
        return attribute["value"]


class OrionIntegerField(models.IntegerField, OrionField):
    valid_orion_types = ("Integer", "Number")


class OrionURLField(models.URLField, OrionField):
    valid_orion_types = ("Text", "String")


class OrionCharField(models.CharField, OrionField):
    valid_orion_types = ("Text", "String")


class OrionTextField(models.TextField, OrionField):
    valid_orion_types = ("Text", "String")


class OrionFloatField(models.FloatField, OrionField):
    valid_orion_types = ("decimal", "integer", "Number")


class OrionDateTimeField(models.DateTimeField, OrionField):
    valid_orion_types = ("DateTime", "Text", "String")

    def extract_from_json(self, json_data):
        attribute = super().extract_from_json(json_data)
        if attribute is '':
            attribute = None
        return attribute


class OrionJSONField(JSONField, OrionField):
    valid_orion_types = ("StructuredValue", )


class OrionDecimalField(models.DecimalField, OrionField):
    valid_orion_types = ("decimal", "integer", "Number")


class OrionBooleanField(models.BooleanField, OrionField):
    valid_orion_types = ("Boolean", )


class OrionListField(ArrayField, OrionField):
    valid_orion_types = ("List",)

    def __init__(self, *args, **kwargs):
        super().__init__(base_field=JSONField(), *args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["base_field"]
        return name, path, args, kwargs


class OrionRef(OrionCharField):
    valid_orion_types = ("Text", "String")
    default_max_length = 1024

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = min(kwargs.get("max_length", self.default_max_length), self.default_max_length)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if kwargs["max_length"] >= self.default_max_length:
            del kwargs["max_length"]
        return name, path, args, kwargs


class OrionRefList(ArrayField, OrionField):
    valid_orion_types = ("List",)

    def __init__(self, *args, **kwargs):
        kwargs["base_field"] = OrionRef()
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["base_field"]
        return name, path, args, kwargs


class OrionCoordinatesField(ArrayField, OrionField):
    valid_orion_types = "geo:json"

    def extract_from_json(self, json_data):
        attribute = json_data.get(self.name)
        if attribute is None:
            raise KeyError(self.name + " Not included in data")
        if attribute["type"] not in self.valid_orion_types:
            raise Exception("Django orion field %s is not valid type: %s",
                            self.name, attribute["type"], self.valid_orion_types)

        return attribute["value"]['coordinates']

    def __init__(self, *args, **kwargs):
        kwargs["base_field"] = models.DecimalField(max_digits=11, decimal_places=8)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["base_field"]
        return name, path, args, kwargs
