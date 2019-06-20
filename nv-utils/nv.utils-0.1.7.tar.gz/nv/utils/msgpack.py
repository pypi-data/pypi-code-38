"""
This adds support to Python datetime objects.
"""

import datetime

from decimal import Decimal
from functools import partial
from collections import namedtuple

import msgpack

from .parsers import parse_date, parse_time, parse_datetime, parse_duration, format_duration


__all__ = ['pack', 'packb', 'unpack', 'unpackb', 'dump', 'dumps', 'load', 'loads', ]


TE = namedtuple('TE', ('mark', 'encoder', 'decoder'))
DEFAULT_CONTENT_KEY = '__msgpack__'


# Encoders / decoders
def encode_decimal(obj):
    return obj.as_integer_ratio()


def decode_decimal(obj):
    a, b = obj
    return Decimal(a) / Decimal(b)


ENCODING_MATRIX = {
    datetime.date: TE('date', datetime.date.isoformat, parse_date),
    datetime.time: TE('time', datetime.time.isoformat, parse_time),
    datetime.datetime: TE('datetime', datetime.datetime.isoformat, parse_datetime),
    datetime.timedelta: TE('timedelta', format_duration, parse_duration),
    Decimal: TE('decimal', encode_decimal, decode_decimal)
}


def get_decoding_matrix(encoding_matrix):
    return {k.mark: k for k in encoding_matrix.values()}


DECODING_MATRIX = get_decoding_matrix(ENCODING_MATRIX)


def encode(obj, matrix):
    entry = matrix.get(type(obj), None)

    if entry:
        return {DEFAULT_CONTENT_KEY: (entry.mark, entry.encoder(obj))}

    return obj


def decode(obj, matrix):

    if isinstance(obj, dict):
        content = obj.get(DEFAULT_CONTENT_KEY, None)

        if content:
            entry_type, content = content
            entry = matrix.get(entry_type, None)

            if entry is None:
                raise TypeError(f"Unable do decode {entry_type}: unknown entry type")

            obj = entry.decoder(content)

    return obj

def packb(obj, **kwargs):
    kwargs['default'] = partial(encode, matrix=ENCODING_MATRIX)
    kwargs.setdefault('use_bin_type', True)
    return msgpack.packb(obj, **kwargs)


def pack(fp, **kwargs):
    kwargs['default'] = partial(encode, matrix=ENCODING_MATRIX)
    kwargs.setdefault('use_bin_type', True)
    return msgpack.pack(fp, **kwargs)


def unpackb(obj, **kwargs):
    kwargs['object_hook'] = partial(decode, matrix=DECODING_MATRIX)
    kwargs.setdefault('raw', False)
    return msgpack.unpackb(obj, **kwargs)


def unpack(fp, **kwargs):
    kwargs['object_hook'] = partial(decode, matrix=DECODING_MATRIX)
    kwargs.setdefault('raw', False)
    return msgpack.unpack(fp, **kwargs)


dump = pack
dumps = packb
load = unpack
loads = unpackb
