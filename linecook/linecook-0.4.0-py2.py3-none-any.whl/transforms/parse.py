# -*- coding: utf-8 -*-
"""
Transforms that parse data from text.
"""
from __future__ import unicode_literals
from future.standard_library import install_aliases

install_aliases()

import json  # noqa
from urllib.parse import parse_qs  # noqa


def json_from_qs(flatten=True):
    """Return tranform that outputs json string from query string."""

    def transform(query_string):
        data = parse_qs(query_string)
        if flatten:
            _flatten_single_element_items(data)
        return json.dumps(data)

    return transform


def _flatten_single_element_items(data):
    for key, value in data.items():
        if isinstance(value, list) and len(value) == 1:
            data[key] = value[0]
