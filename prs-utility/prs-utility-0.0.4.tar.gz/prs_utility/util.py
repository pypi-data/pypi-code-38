from collections import OrderedDict
from urllib.parse import urlencode, quote
from typing import Any, Dict, Union


def buf_to_hex(buf: bytes) -> str:
    return buf.hex()


def hex_to_buf(s_hex: str) -> bytes:
    return bytes.fromhex(s_hex)


def dump_buf(buf: bytes, dump: bool = True) -> Union[bytes, str]:
    return buf_to_hex(buf) if dump else buf


def quote_qs(
        string: str,
        safe: str = '',
        encoding: str = 'utf-8',
        errors: str = 'strict'
) -> str:
    return quote(string, safe=safe, encoding=encoding, errors=errors)


def get_sorted_qs(data: Dict[str, Any]) -> str:
    sorted_dict = OrderedDict(sorted(data.items()))
    # replace True => true, False => false
    for k, v in sorted_dict.items():
        if v is True:
            sorted_dict[k] = 'true'
        elif v is False:
            sorted_dict[k] = 'false'
    return urlencode(sorted_dict, quote_via=quote_qs)


def remove_prefix_0x(s: str) -> str:
    """remove prefix '0x' or '0X' from string s

    :param s: str

    :return: str, the substring which remove the prefix '0x' or '0X'
    """
    if s[:2].lower() == '0x':
        s = s[2:]
    return s
