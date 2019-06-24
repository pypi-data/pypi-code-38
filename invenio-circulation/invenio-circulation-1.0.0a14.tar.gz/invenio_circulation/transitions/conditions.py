# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio Circulation transitions conditions."""

from flask import current_app


def is_same_location(item_pid, input_location_pid):
    """Return True if item belonging location is same as input parameter."""
    item_location_pid = current_app.config.get(
        'CIRCULATION_ITEM_LOCATION_RETRIEVER'
    )(item_pid)

    return input_location_pid == item_location_pid
