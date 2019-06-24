# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Circulation Item JSON Resolver module."""

import jsonresolver
from werkzeug.routing import Rule


@jsonresolver.hookimpl
def jsonresolver_loader(url_map):
    """Resolve the item reference."""
    from flask import current_app
    resolving_path = current_app.config.get(
        "CIRCULATION_ITEM_RESOLVING_PATH") or "/"
    url_map.add(Rule(
        resolving_path,
        endpoint=current_app.config.get('CIRCULATION_ITEM_RESOLVER_ENDPOINT'),
        host=current_app.config.get('JSONSCHEMAS_HOST')))
