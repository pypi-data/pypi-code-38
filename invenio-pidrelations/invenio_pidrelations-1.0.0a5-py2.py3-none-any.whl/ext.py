# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module that adds PID relations to the Invenio-PIDStore module."""

from __future__ import absolute_import, print_function

from werkzeug.utils import cached_property

from invenio_pidrelations import config


class _InvenioPIDRelationsState(object):
    """InvenioPIDRelations REST state."""

    def __init__(self, app):
        """Initialize state."""
        self.app = app

    @cached_property
    def relation_types(self):
        return self.app.config.get('PIDRELATIONS_RELATION_TYPES', {})


class InvenioPIDRelations(object):
    """Invenio-PIDRelations extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions['invenio-pidrelations'] = _InvenioPIDRelationsState(app)

    def init_config(self, app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith('PIDRELATIONS_'):
                app.config.setdefault(k, getattr(config, k))
