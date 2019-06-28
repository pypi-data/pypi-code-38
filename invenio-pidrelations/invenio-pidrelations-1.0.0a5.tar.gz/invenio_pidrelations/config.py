# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module that adds PID relations to the Invenio-PIDStore module."""

from collections import namedtuple

RelationType = namedtuple('RelationType',
                          ['id', 'name', 'label', 'api', 'schema'])

PIDRELATIONS_RELATION_TYPES = [
    RelationType(0, 'version', 'Version',
                 'invenio_pidrelations.contrib.versioning:PIDNodeVersioning',
                 'invenio_pidrelations.serializers.schemas.RelationSchema'),
    RelationType(1, 'record_draft', 'Record Draft',
                 'invenio_pidrelations.contrib.draft:PIDNodeDraft',
                 'invenio_pidrelations.serializers.schemas.RelationSchema'),
]
