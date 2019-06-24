# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Helper proxy to the state object."""

from __future__ import absolute_import, print_function

from flask import current_app
from werkzeug.local import LocalProxy

current_circulation = LocalProxy(
    lambda: current_app.extensions['invenio-circulation']
)
"""Helper proxy to circulation state object."""
