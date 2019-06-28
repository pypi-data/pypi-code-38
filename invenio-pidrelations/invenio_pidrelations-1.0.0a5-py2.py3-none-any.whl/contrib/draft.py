# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Records integration for PIDRelations."""

from ..api import PIDNode
from ..utils import resolve_relation_type_config


class PIDNodeDraft(PIDNode):
    """API for PID draft relations.

    parents (max: 1): a record PID (potentially RESERVED).
    children (max: 1): a draft record PID.

    A common submission workflow is to have a draft record which can be
    published. The published record has its own separate PID. See
    invenio-deposit for more details.
    Typical scenario is that of creating a new Deposit which is linked to a
    not-yet published record PID (PID status is RESERVED).

    NOTE: This relation exists because usually newly created records are not
    immediately stored inside the database (they have no `RecordMetada`). This
    leads to having deposits that are hanging onto no actual record and only
    possess "soft" links to their records' PIDs through metadata.
    """

    def __init__(self, pid):
        """Create a record draft API.

        :param pid: either the published record PID or the deposit PID.
        """
        self.relation_type = resolve_relation_type_config('record_draft')
        super(PIDNodeDraft, self).__init__(
            pid=pid, relation_type=self.relation_type,
            max_parents=1, max_children=1
        )
