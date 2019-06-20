from configparser import ConfigParser


__all__ = ['parse_boolean', 'parse_strict_boolean', 'DEFAULT_BOOLEAN_STATES', 'STRICT_BOOLEAN_STATES']


STRICT_BOOLEAN_STATES = {
    'TRUE': True,
    'FALSE': False,
}

DEFAULT_BOOLEAN_STATES = ConfigParser.BOOLEAN_STATES


class NotFound:
    pass


def parse_boolean(obj, strict=False, boolean_states=DEFAULT_BOOLEAN_STATES, force=False, default=None):

    boolean_states = STRICT_BOOLEAN_STATES if strict else boolean_states

    assert boolean_states, "Boolean states must be a mapping from potential objects to booleans"

    if isinstance(obj, bool):
        return obj

    resp = boolean_states.get(obj.upper() if isinstance(obj, str) else obj, NotFound)

    if resp is NotFound:
        if force:
            resp = bool(obj)
        elif default is not None:
            resp = default

    if resp is NotFound:
        raise TypeError(f"Unable to parse to boolean (strict={strict}, force={force}): {obj!s}")

    return resp


def parse_strict_boolean(obj, default=None):
    return parse_boolean(obj, strict=True, force=False, default=default)
