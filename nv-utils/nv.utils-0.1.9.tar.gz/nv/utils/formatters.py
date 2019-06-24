from collections import ChainMap
from collections.abc import Mapping
from functools import partial
import string
from typing import Tuple

from .parsers import parse_structure


class SafeFormattingDict(dict):
    # This dictionary allows to keep formatting fields with missing keys unchanged
    def __missing__(self, key):
        return f"{{{key}}}"


class CleanUpDict(dict):
    def __missing__(self, key):
        return ""


class MissingKeysDict(SafeFormattingDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._missing_keys = set()

    def __missing__(self, key):
        self._missing_keys.add(key)
        return f"{{{key}}}"

    def missing_keys(self) -> set:
        return self._missing_keys


class SafeFormatter(string.Formatter):
    def check_unused_args(self, used_args, args, kwargs):
        # This function is supposed to raise problems when a key is not used, but was overwritten to do nothing
        pass


def safe_format(s: str, dic: Mapping, missing=True) -> str:
    """
    Default Python formatter that does not raise error if dict has entries that were not used.
    
    If missing is True,
    entries that were not found in dict are skipped.
    :param s: string to be formatted
    :param dic: formatting entries
    :param missing: if True, missing entries are skipped.
    :return: formatted text
    """
    return SafeFormatter().vformat(s, None, SafeFormattingDict(dic) if missing else dic)


def missing_keys(s: str, dic: Mapping = None) -> set:
    """
    Helper for safe_format that returns keys that were not included in dic. This is useful to prepare a list of
    variables needed for parsing a template string.
    :param s: string to be formatted
    :param dic: map with formatting entries
    :return: set with all entries that were not found in dic.
    """
    dic = MissingKeysDict(dic)
    SafeFormatter().vformat(s, None, dic)
    return dic.missing_keys()


def safe_format_missing(s: str, dic: Mapping) -> Tuple[str, set]:
    """
    This is a combination of safe_format and missing_keys. This is a shortcut that parses that string once with
    variables that were in dic, returning as a result the partially formatted string and a list with missing entries.
    :param s: string to be formatted
    :param dic: map with formatting entries
    :return: tuple with partially formatted string and set with missing entries
    """
    dic = MissingKeysDict(dic)
    result = SafeFormatter().vformat(s, None, dic)
    return result, dic.missing_keys()


def format_structure(struct, dic, defaults=None, missing=False, clean_up=False):
    """
    Applies python formatting to strings in a structure (i.e. strings in any combination of nested sequences and/or
    mapping).
    :param struct: nested mappings or sequences with strings as content. This is probably what you get when parsing a
    json or yaml. This function looks for '{key}' in strings inside of a structure and replace them by value as per the
    dictionary supplied.
    :param dic: variables to look for in a dictionary or any other mapping.
    :param defaults: variables to use as a fallback when the entry is not found in dic.
    :param missing: keeps missing entries intact if not found in dic and defaults, otherwise raises exception.
    :param clean_up: if True, all empty entries are removed (e.g. '', (), {}, etc.)
    :return: formatted structure
    """

    if clean_up:
        dict_cls = CleanUpDict
    elif missing:
        dict_cls = SafeFormattingDict
    else:
        dict_cls = dict

    dic = ChainMap(dic, dict_cls(defaults) if defaults else dict_cls(dic))
    
    # missing will be addressed by dict_class, so we are forcing to use dict 
    str_parser = partial(safe_format, dic=dic, missing=False)

    return parse_structure(struct, str_parser=str_parser, clean_up=clean_up)
