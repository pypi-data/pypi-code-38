"""
YAML serializer.

Requires PyYaml (https://pyyaml.org/), but that's checked for in __init__.
"""

import collections
import decimal
from io import StringIO

import yaml

from server.core.serializers.base import DeserializationError
from server.core.serializers.python import (
    Deserializer as PythonDeserializer, Serializer as PythonSerializer,
)
from server.db import models

# Use the C (faster) implementation if possible
try:
    from yaml import CSafeLoader as SafeLoader
    from yaml import CSafeDumper as SafeDumper
except ImportError:
    from yaml import SafeLoader, SafeDumper


class ServerSafeDumper(SafeDumper):
    def represent_decimal(self, data):
        return self.represent_scalar('tag:yaml.org,2002:str', str(data))

    def represent_ordered_dict(self, data):
        return self.represent_mapping('tag:yaml.org,2002:map', data.items())


ServerSafeDumper.add_representer(decimal.Decimal, ServerSafeDumper.represent_decimal)
ServerSafeDumper.add_representer(collections.OrderedDict, ServerSafeDumper.represent_ordered_dict)


class Serializer(PythonSerializer):
    """Convert a queryset to YAML."""

    internal_use_only = False

    def handle_field(self, obj, field):
        # A nasty special case: base YAML doesn't support serialization of time
        # types (as opposed to dates or datetimes, which it does support). Since
        # we want to use the "safe" serializer for better interoperability, we
        # need to do something with those pesky times. Converting 'em to strings
        # isn't perfect, but it's better than a "!!python/time" type which would
        # halt deserialization under any other language.
        if isinstance(field, models.TimeField) and getattr(obj, field.name) is not None:
            self._current[field.name] = str(getattr(obj, field.name))
        else:
            super().handle_field(obj, field)

    def end_serialization(self):
        yaml.dump(self.objects, self.stream, Dumper=ServerSafeDumper, **self.options)

    def getvalue(self):
        # Grandparent super
        return super(PythonSerializer, self).getvalue()


def Deserializer(stream_or_string, **options):
    """Deserialize a stream or string of YAML data."""
    if isinstance(stream_or_string, bytes):
        stream_or_string = stream_or_string.decode()
    if isinstance(stream_or_string, str):
        stream = StringIO(stream_or_string)
    else:
        stream = stream_or_string
    try:
        yield from PythonDeserializer(yaml.load(stream, Loader=SafeLoader), **options)
    except (GeneratorExit, DeserializationError):
        raise
    except Exception as exc:
        raise DeserializationError() from exc
