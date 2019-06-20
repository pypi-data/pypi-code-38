import datetime
from decimal import Decimal
from functools import lru_cache

from .dateparse import parse_datetime, parse_date, parse_time, parse_duration
from .boolean import parse_strict_boolean, parse_boolean

__all__ = ['guess_type', 'cast', 'safe_cast', 'TYPE_GUESS_ORDER', 'TYPE_GUESS_ORDER_DECIMAL', 'DEFAULT_PARSERS',
           'DEFAULT_CONFIG_PARSERS']


TYPE_GUESS_ORDER = (
    int,
    float,
    datetime.datetime,
    datetime.date,
    datetime.time,
    datetime.timedelta,
    bool,
    str
)

TYPE_GUESS_ORDER_DECIMAL = (
    int,
    Decimal,
    float,
    datetime.datetime,
    datetime.date,
    datetime.time,
    datetime.timedelta,
    bool,
    str
)

DEFAULT_PARSERS = {
    bool: parse_strict_boolean,
    datetime.datetime: parse_datetime,
    datetime.date: parse_date,
    datetime.time: parse_time,
    datetime.timedelta: parse_duration,
}


DEFAULT_CONFIG_PARSERS = {
    bool: parse_boolean,
    datetime.datetime: parse_datetime,
    datetime.date: parse_date,
    datetime.time: parse_time,
    datetime.timedelta: parse_duration,
}


def _cast_attempt(obj, to_type):
    """
    Attempts to cast obj to cast_type (a type or any sort of callable parser that must return a valid output or raise an error)
    When successful, it should return the cast type and the cast_value (which is an useful byproduct). If failed, it
    returns None and the original object.
    """
    try:
        resp = to_type(obj) if obj is not None else to_type()
    except (TypeError, ValueError):
        return obj, None

    # If we get None from a valid input, it means that our parsing has not went through
    if resp is None and obj is not None:
        return obj, None

    return resp, type(resp)


@lru_cache(1)
def _include_item_before(item_to_include, item_to_search, lst):
    # Copy to avoid mutation
    lst = list(lst)
    try:
        index = lst.index(item_to_search)
    except ValueError:
        return lst

    return lst[:index] + [item_to_include] + lst[index:]


def _substitute_item(item_to_be_replaced, item_to_include, lst):
    # Copy to avoid mutation
    lst = list(lst)
    try:
        index = lst.index(item_to_be_replaced)
    except ValueError:
        return lst

    return lst[:index] + [item_to_include] + lst[index + 1:]


def guess_type(obj, prefer_decimal=False, strict_boolean=True, type_guess_order=TYPE_GUESS_ORDER, parsers=None):
    """
    Tries to guess the most appropriate type for an object (typically a string) according to a preferred list.
    In essence, what this does is attempt to cast 'obj' into the first type (or callable) that fits. By fitting
    it means returning a valid object (instead of raising a ValueError).

    This is a bit tricky for boolean types, so we stick to 'TRUE/FALSE' (and lower case variations) for the default
    case but we offer the alternative for a more flexible boolean interpretation by setting strict_boolean to False.

    Bear in mind that strict_boolean is overridden by whatever you define as a bool parser when custom parsers
    are used in 'parsers' kwarg.

    We also include a convenience to force numbers to be parsed as Decimal numbers rather than floats.
    """

    # Short-circuit for None
    if obj is None:
        return None, None

    parsers = parsers or (DEFAULT_PARSERS if strict_boolean else DEFAULT_CONFIG_PARSERS)

    if prefer_decimal:
        type_guess_order = TYPE_GUESS_ORDER_DECIMAL if type_guess_order is TYPE_GUESS_ORDER \
            else _include_item_before(Decimal, float, type_guess_order)

    for type_guess in type_guess_order:

        parser = parsers.get(type_guess, type_guess)
        resp, _type = _cast_attempt(obj, parser)

        # If returned type is equal to type guess, casting has been successful
        if _type is type_guess:
            return _type, resp

    return None, obj


def cast(obj, to_type, parsers=None):

    if isinstance(obj, to_type):
        return obj

    parsers = parsers or DEFAULT_PARSERS

    parser = parsers.get(to_type, to_type)

    resp, _type = _cast_attempt(obj, parser)

    if _type is None:
        raise TypeError(f"Unable to cast object into {to_type!s} using {parser!s}: {obj}")

    return resp


def safe_cast(obj, to_type):
    try:
        return cast(to_type, obj)
    except TypeError:
        return obj
