import re
import six
from collections import namedtuple


# regex to convert from camelCase to snake_case
_reg = re.compile(r'(?!^)(?<!_)([A-Z])')


def siren_to_dict(o):
    return {
        attr: getattr(o, attr)
        for attr in dir(o)
        if attr[:1] != '_' and not callable(getattr(o, attr))
    }


def siren_to_entity(o):
    """
    Helper method that converts a siren entity into a namedtuple
    """
    def value_to_entity(v):
        return siren_to_entity(v) if isinstance(v, dict) else v

    # pypermedia does not do recursive translation
    # so we might get a mix of objects or dicts in here
    attrs = siren_to_dict(o) if not isinstance(o, dict) else o
    attrs = {
        to_snake_case(key): value_to_entity(value)
        for key, value in six.iteritems(attrs)
    }
    return namedtuple(o.__class__.__name__, sorted(attrs))(**attrs)


def to_snake_case(s):
    # need to sanitise the string as in some cases the key might look like
    # 'Data Access' or 'Data Sensitivity'
    return _reg.sub(r'_\1', s.replace(' ', '_')).lower()