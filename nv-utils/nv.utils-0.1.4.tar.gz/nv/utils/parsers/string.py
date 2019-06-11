from .casting import DEFAULT_PARSERS, TYPE_GUESS_ORDER
from .casting import guess_type


__all__ = ['parse_str']


def parse_str(s, allow_blank=True, prefer_decimal=False, strict_boolean=True, type_guess_order=None, parsers=None):
    type_guess_order = type_guess_order or TYPE_GUESS_ORDER
    parsers = parsers or DEFAULT_PARSERS

    if s is '':
        return s if allow_blank else None

    _, resp = guess_type(s, prefer_decimal=prefer_decimal, strict_boolean=strict_boolean, type_guess_order=type_guess_order, parsers=parsers)

    return resp



