"""Base resource containing properties shared by all spatial resources"""
from __future__ import absolute_import

import json
from collections import OrderedDict

from lfview.resources import files
import properties.extras
from six import string_types


def to_hex(value):
    """Converts RGB tuple to hex string"""
    hex_values = (hex(i).lstrip('0x').upper().ljust(2, '0') for i in value)
    return '#{}'.format(''.join(hex_values))


def from_hex(value):
    """Converts RGB tuple to hex string"""
    color_str = value.lstrip('#')
    if len(color_str) != 6:
        raise ValueError('Invalid hex color: {}'.format(value))
    for digit in color_str:
        if digit.upper() not in '0123456789ABCDEF':
            raise ValueError('Invalid hex color: {}'.format(value))
    int_values = tuple(
        int(color_str[i:i + 6 // 3], 16) for i in range(0, 6, 6 // 3)
    )
    return int_values


def snapshot_serializer(val, **kwargs):
    """Serializer function that returns a JSON string if snapshot=True"""
    snapshot = kwargs.get('snapshot', False)
    val = val.serialize(**kwargs)
    if snapshot:
        val = json.dumps(val)
    return val


def get_snapshot_deserializer(instance_class):
    """Deserializer that accepts JSON strings

    This must be initialized with the instance_class.
    """

    def snapshot_deserializer(val, **kwargs):
        kwargs.update({'strict': True})
        if isinstance(val, string_types):
            val = json.loads(val)
        return instance_class.deserialize(val, **kwargs)

    return snapshot_deserializer


class InstanceSnapshot(properties.Instance):
    """Instance property that can serialize to JSON string

    This property type inherits from :class:`properties.Instance`.
    However, it overrides the serializer and deserializer with custom
    methods that allow serialization to JSON string. To access this
    behavior, pass :code:`snapshot=True` key word argument into
    :code:`serialize`.
    """

    class_info = 'an instance saved as a JSON string'

    def __init__(self, doc, instance_class, **kwargs):
        if 'serializer' in kwargs or 'deserializer' in kwargs:
            raise ValueError(
                'InstanceSnapshots must not override serializer/deserializer'
            )
        kwargs.update(
            {
                'serializer': snapshot_serializer,
                'deserializer': get_snapshot_deserializer(instance_class),
            }
        )
        super(InstanceSnapshot, self).__init__(doc, instance_class, **kwargs)


class ShortString(properties.String):
    """String property with maximum length

    **Available keywords** (in addition to those inherited from
    :class:`properties.String`):

    * **max_length** - If specified, the length of the string is
      validated to be less than or equal to this value.
    """

    @property
    def max_length(self):
        """Integer value for maximum length of string"""
        return getattr(self, '_max_length', None)

    @max_length.setter
    def max_length(self, value):
        self._max_length = int(value)

    def validate(self, instance, value):
        value = super(ShortString, self).validate(instance, value)
        if self.max_length and len(value) > self.max_length:
            self.error(
                instance=instance,
                value=(
                    value if len(value) < 14 else
                    '{}...{}'.format(value[:5], value[-5:])
                ),
                extra='(Length is {})'.format(len(value)),
            )
        return value

    @property
    def info(self):
        info = super(ShortString, self).info
        if self.max_length:
            info += ' and less than {} characters'.format(self.max_length)
        return info


class _BaseResource(files.base._BaseUIDModel):
    """Base class for all high-level API resources"""

    _REGISTRY = OrderedDict()

    name = ShortString(
        'Name or title of resource',
        required=False,
        max_length=300,
    )
    description = ShortString(
        'Description of resource',
        required=False,
        max_length=5000,
    )
