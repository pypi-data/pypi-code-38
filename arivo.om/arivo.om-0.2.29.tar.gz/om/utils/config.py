# coding=utf-8
from __future__ import unicode_literals

from socket import gethostname

import yaml

try:
    import __builtin__
except ImportError:
    import builtins

    __builtin__ = builtins

import logging
import os

import related
import six


def _save_cast(obj, key, to_type, default):
    try:
        return to_type(obj[key])
    except (ValueError, TypeError, KeyError):
        return default


def int(key, default=0):
    assert isinstance(default, (__builtin__.int, __builtin__.float)), "default argument must be of type int or float"
    return _save_cast(os.environ, key, __builtin__.int, __builtin__.int(default))


def float(key, default=0.0):
    assert isinstance(default, (__builtin__.int, __builtin__.float)), "default argument must be of type int or float"
    return _save_cast(os.environ, key, __builtin__.float, __builtin__.float(default))


def string(key, default=""):
    assert isinstance(default, six.string_types), "default argument must be of type string"
    res = os.environ.get(key, default)
    invalid_chars = "\"' "
    res = res.strip(invalid_chars)
    return res


def bool(key, default=False):
    assert isinstance(default, __builtin__.bool), "default argument must be of type bool"
    val = get(key, None)
    if val is None:
        return default
    return val.upper().strip('\'" .,;-_') in ["T", "TRUE", "1", "Y", "YES", "J", "JA"]


def get(key, default=""):
    return os.environ.get(key, default)


def log_level():
    log_levels = {
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
        "WARN": logging.WARNING,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "ERR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
        "CRIT": logging.CRITICAL,
        "FATAL": logging.FATAL
    }
    return log_levels.get(os.environ.get("LOG_LEVEL", "INFO").upper(), logging.INFO)


def from_yaml(path, cls, loader=yaml.Loader, to_related=True):
    if os.path.isdir(path):
        logging.error("config file is a directory, umad?")
        return cls()
    if not os.path.isfile(path):
        return cls()
    with open(path) as f:
        y = f.read().strip()

    d = related.from_yaml(y, loader_cls=loader)
    if to_related:
        return related.to_model(cls, d)
    else:
        return d


def version():
    version = string("VERSION", "")
    if not version:
        if os.path.isfile("VERSION"):
            with open("VERSION", "r") as f:
                version = f.read()
    if not version:
        version = "unknown"
    return version


def resource():
    resource = string("AUTH_RESOURCE", "")
    if not resource:
        resource = gethostname()
    return resource
