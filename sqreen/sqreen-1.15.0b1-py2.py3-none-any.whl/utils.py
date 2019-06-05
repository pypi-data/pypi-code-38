# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Various utils
"""
import json
import sys
from functools import WRAPPER_ASSIGNMENTS
from inspect import isclass
from logging import getLogger
from operator import methodcaller

from ._vendors.ipaddress import (
    ip_address as _ip_address,
    ip_network as _ip_network,
)

LOGGER = getLogger(__name__)
PYTHON_VERSION = sys.version_info[0]


if PYTHON_VERSION == 2:
    ALL_STRING_CLASS = basestring  # noqa
    STRING_CLASS = str
    UNICODE_CLASS = unicode  # noqa
elif PYTHON_VERSION == 3:
    ALL_STRING_CLASS = str
    STRING_CLASS = str
    UNICODE_CLASS = str
NONE_TYPE = type(None)


HAS_ASYNCIO = sys.version_info >= (3, 4)


def is_string(value):
    """ Check if a value is a valid string, compatible with python 2 and python 3

    >>> is_string('foo')
    True
    >>> is_string(u'✌')
    True
    >>> is_string(42)
    False
    >>> is_string(('abc',))
    False
    """
    return isinstance(value, ALL_STRING_CLASS)


def is_unicode(value):
    """ Check if a value is a valid unicode string, compatible with python 2 and python 3

    >>> is_unicode(u'foo')
    True
    >>> is_unicode(u'✌')
    True
    >>> is_unicode(b'foo')
    False
    >>> is_unicode(42)
    False
    >>> is_unicode(('abc',))
    False
    """
    return isinstance(value, UNICODE_CLASS)


def to_latin_1(value):
    """ Return the input string encoded in latin1 with replace mode for errors
    """
    return value.encode("latin-1", "replace")


def is_json_serializable(value):
    """ Check that a single value is json serializable
    """
    return isinstance(value, (ALL_STRING_CLASS, NONE_TYPE, bool, int, float))


def update_wrapper(wrapper, wrapped):
    """ Update wrapper attribute to make it look like wrapped function.
    Don't use original update_wrapper because it can breaks if wrapped don't
    have all attributes.
    """
    for attr in WRAPPER_ASSIGNMENTS:
        if hasattr(wrapped, attr):
            setattr(wrapper, attr, getattr(wrapped, attr))
    return wrapper


###
# Raven configuration
###


def _raven_ignoring_handler(logger, *args, **kwargs):
    """ Ignore all logging messages from sqreen.* loggers, effectively
    disabling raven to log sqreen log messages as breadcrumbs
    """
    try:
        if logger.name.startswith("sqreen"):
            return True
    except Exception:
        LOGGER.warning("Error in raven ignore handler", exc_info=True)


def configure_raven_breadcrumbs():
    """ Configure raven breadcrumbs logging integration if raven is present
    """
    try:
        from raven import breadcrumbs
    except ImportError:
        return

    # Register our logging handler to stop logging sqreen log messages
    # as breadcrumbs
    try:
        breadcrumbs.register_logging_handler(_raven_ignoring_handler)
    except Exception:
        LOGGER.warning("Error while configuring breadcrumbs", exc_info=True)


###
# JSON Encoder
###


def qualified_class_name(obj):
    """ Return the full qualified name of the class name of obj in form of
    `full_qualified_module.class_name`
    """
    if isclass(obj):
        instance_class = obj
    else:
        instance_class = obj.__class__

    return ".".join([instance_class.__module__, instance_class.__name__])


def django_user_conversion(obj):
    """ Convert a Django user either by returning USERNAME_FIELD or convert
    it to str.
    """
    if hasattr(obj, "USERNAME_FIELD"):
        return getattr(obj, getattr(obj, "USERNAME_FIELD"), None)
    else:
        return str(obj)


class CustomJSONEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        super(CustomJSONEncoder, self).__init__(*args, **kwargs)

        self.mapping = {}

        self.mapping["bson.objectid.ObjectId"] = str
        self.mapping[
            "django.contrib.auth.models.AbstractUser"
        ] = django_user_conversion

        # Convert datetime to isoformat, compatible with Node Date()
        self.mapping["datetime.datetime"] = methodcaller("isoformat")

        self.mapping["sqreen._vendors.ipaddress.IPv4Address"] = str
        self.mapping["sqreen._vendors.ipaddress.IPv6Address"] = str

    def default(self, obj):
        """ Return the repr of unkown objects
        """
        if type(obj) == type:
            instance_class = obj
        else:
            instance_class = obj.__class__

        # Manually do isinstance without needed to have a reference to the class
        for klass in instance_class.__mro__:
            qualified_name = qualified_class_name(klass)

            if qualified_name in self.mapping:
                try:
                    return self.mapping[qualified_name](obj)
                except Exception:
                    msg = "Error converting an instance of type %r"
                    LOGGER.warning(msg, obj.__class__, exc_info=True)

        # If we don't, or if we except, fallback on repr
        return repr(obj)


def ip_address(address):
    return _ip_address(UNICODE_CLASS(address))


def ip_network(address, strict=True):
    return _ip_network(UNICODE_CLASS(address), strict=strict)
