# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""PID relations utility functions."""

from __future__ import absolute_import, print_function

import six
from flask import current_app
from werkzeug.utils import import_string


def obj_or_import_string(value, default=None):
    """Import string or return object.

    :params value: Import path or class object to instantiate.
    :params default: Default object to return if the import fails.
    :returns: The imported object.
    """
    if isinstance(value, six.string_types):
        return import_string(value)
    elif value:
        return value
    return default


def resolve_relation_type_config(value):
    """Resolve the relation type to config object.

    Resolve relation type from string (e.g.:  serialization) or int (db value)
    to the full config object.
    """
    relation_types = current_app.config['PIDRELATIONS_RELATION_TYPES']
    if isinstance(value, six.string_types):
        try:
            obj = next(rt for rt in relation_types if rt.name == value)
        except StopIteration:
            raise ValueError("Relation name '{0}' is not configured.".format(
                value))

    elif isinstance(value, int):
        try:
            obj = next(rt for rt in relation_types if rt.id == value)
        except StopIteration:
            raise ValueError("Relation ID {0} is not configured.".format(
                value))
    else:
        raise ValueError("Type of value '{0}' is not supported for resolving.".
                         format(value))
    api_class = obj_or_import_string(obj.api)
    schema_class = obj_or_import_string(obj.schema)
    return obj.__class__(obj.id, obj.name, obj.label, api_class, schema_class)
