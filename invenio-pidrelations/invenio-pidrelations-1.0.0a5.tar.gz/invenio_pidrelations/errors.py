# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Errors for persistent identifiers."""

from __future__ import absolute_import, print_function


class PIDRelationError(Exception):
    """Base class for PIDRelations errors."""


class PIDRelationConsistencyError(PIDRelationError):
    """Base class for relation consistency errors."""
