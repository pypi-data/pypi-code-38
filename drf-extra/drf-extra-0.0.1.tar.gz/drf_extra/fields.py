from datetime import datetime

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class MetadataField(serializers.JSONField):
    """
    JSON field for metadata serialization.
    """

    def to_internal_value(self, data):
        data = super().to_internal_value(data)

        if data is None or isinstance(data, dict):
            return data
        else:
            raise serializers.ValidationError(
                _('Invalid metadata. Must be a valid object.'))


class TimestampField(serializers.Field):
    """
    Timestamp field for datetime serialization.
    """

    def __init__(self, *args, **kwargs):
        self.multiplier = kwargs.pop('multiplier', 1000)
        super().__init__(*args, **kwargs)

    def to_representation(self, obj):
        try:
            return int(obj.timestamp() * self.multiplier)
        except AttributeError:
            return None

    def to_internal_value(self, obj):
        try:
            date = datetime.strptime(str(obj), '%Y-%m-%dT%H:%M:%SZ').timestamp()
        except ValueError:
            raise serializers.ValidationError(
                _('Incorrect date format, expected ISO 8601.'))

        return datetime.fromtimestamp(int(date))
