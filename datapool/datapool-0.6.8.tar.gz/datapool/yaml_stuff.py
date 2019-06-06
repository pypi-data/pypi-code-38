# encoding: utf-8
from __future__ import print_function, division, absolute_import

from datetime import datetime
import os

from ruamel import yaml

from .bunch import Bunch
from .errors import ConsistencyError, FormatError
from .utils import iter_to_list


def load_yaml_and_bunchify(path):
    path = os.path.abspath(path)
    with open(path, "rb") as fh:
        data = yaml.load(fh)
        return bunchify(data)


def bunchify(obj):
    if isinstance(obj, dict):
        obj = {k: bunchify(v) for (k, v) in obj.items()}
        return Bunch(obj)
    elif isinstance(obj, list):
        obj = [bunchify(item) for item in obj]
    elif isinstance(obj, tuple):
        obj = tuple(bunchify(item) for item in obj)
    elif isinstance(obj, set):
        obj = set(bunchify(item) for item in obj)
    return obj


def parse_datetime(s):
    if isinstance(s, datetime):
        return s
    if not isinstance(s, str):
        raise FormatError("invalid datetime format")
    for fmt_string in ("%Y/%m/%d %H:%M:%S", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt_string)
        except ValueError:
            continue
    raise FormatError("invalid datetime format: could not parse {!r}".format(s))


def is_datetime(s):
    try:
        parse_datetime(s)
    except FormatError:
        return False
    return True


@iter_to_list
def check_yaml_fields_exist(bunch, path, check_attributes):
    """
    "bunch" is a Bunch object holding data, eg site data.
    "path" is the location of the yaml file on on the file system, we need this for reporting
           errors
    "check_attributes" is a list of strings. every string may containt "." to check for
                       chained attributes.
    """

    already_failed = set()

    for attribute in check_attributes:

        if "." in attribute:
            prefix, __ = attribute.rsplit(".", 1)
            # if we already complained about parent we skip this check:
            if prefix in already_failed:
                continue

        temp_bunch = bunch
        for part in attribute.split("."):
            try:
                temp_bunch = temp_bunch[part]
            except KeyError:
                # we record attribute alone, makes testing easier:
                already_failed.add(attribute)
                if "." in attribute:
                    parent, field = attribute.rsplit(".", 1)
                    msg = "{}: attribute {} has no field '{}'".format(
                        path, parent, field
                    )
                    yield ConsistencyError(msg)
                else:
                    yield ConsistencyError(
                        "{} has no field '{}'".format(path, attribute)
                    )
                break
