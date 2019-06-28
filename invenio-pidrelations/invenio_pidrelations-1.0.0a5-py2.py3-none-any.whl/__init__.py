# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module that adds PID relations to the Invenio-PIDStore module."""

from __future__ import absolute_import, print_function

from .ext import InvenioPIDRelations
from .version import __version__

__all__ = ('__version__', 'InvenioPIDRelations')
