#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Utilities for common metadata tools."""
import uuid
import json
from hashlib import md5
from datetime import datetime, date
from peewee import DateTimeField, DateField, text_type
from dateutil import parser

# pylint: disable=invalid-name
unicode_type = text_type
# pylint: enable=invalid-name


def index_hash(*args):
    """
    Generate a hash for all the arguments passed.

    This is used to combine multiple unique IDs into a single string.
    """
    arg_hash = md5()
    for arg in args:
        arg_hash.update(unicode_type(arg).encode('utf-8'))
    return arg_hash.hexdigest()


def date_converts(date_obj):
    """Standardize on converting to date objects."""
    if isinstance(date_obj, (str, unicode_type)):
        return parser.parse(date_obj).date()
    elif isinstance(date_obj, date):
        return date_obj
    elif isinstance(date_obj, int):
        return datetime.utcfromtimestamp(date_obj).date()
    return None


def datetime_now_nomicrosecond():
    """Return now with no microseconds."""
    return datetime.utcnow().replace(microsecond=0)


def datetime_converts(time_obj):
    """Standardize on converting to datetime objects."""
    if isinstance(time_obj, (str, unicode_type)):
        return parser.parse(time_obj).replace(microsecond=0)
    elif isinstance(time_obj, datetime):
        return time_obj.replace(microsecond=0)
    elif isinstance(time_obj, int):
        return datetime.utcfromtimestamp(time_obj).replace(microsecond=0)
    return None


class UUIDEncoder(json.JSONEncoder):
    """UUID Encoder to JSON."""

    # pylint: disable=method-hidden
    def default(self, o):
        """Encode tne UUID by returning it's hex value."""
        if isinstance(o, uuid.UUID):
            # if the obj is uuid, we simply return the value of uuid
            return o.hex
        return json.JSONEncoder.default(self, o)  # pragma: no cover straight out of the docs
    # pylint: enable=method-hidden


class ExtendDateTimeField(DateTimeField):
    """Appends to the DateTimeField to add isoformat from datetime object."""

    # I can't actually prove this works or not...
    def isoformat(self):  # pragma no cover
        """Return the isoformat datetime field."""
        return datetime(
            self.year,
            self.month,
            self.day,
            self.hour,
            self.minute,
            self.second
        ).isoformat()


class ExtendDateField(DateField):
    """Appends to the DateField to add isoformatted date."""

    # I can't actually prove this works or not...
    def isoformat(self):  # pragma no cover
        """Return the isoformat date field."""
        return date(
            self.year,
            self.month,
            self.day
        ).strftime('%Y-%m-%d')
