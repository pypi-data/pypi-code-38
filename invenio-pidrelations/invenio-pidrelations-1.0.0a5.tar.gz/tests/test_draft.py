# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""PIDNodeDraft contribution module tests."""

from __future__ import absolute_import, print_function

import pytest
from invenio_pidstore.models import PersistentIdentifier
from test_helpers import create_pids, with_pid_and_fetched_pid

from invenio_pidrelations.contrib.draft import PIDNodeDraft
from invenio_pidrelations.errors import PIDRelationConsistencyError
from invenio_pidrelations.models import PIDRelation
from invenio_pidrelations.utils import resolve_relation_type_config


@with_pid_and_fetched_pid
def test_record_draft(app, db, build_pid, recids):
    """Test RecordDraft API."""

    parent_pids = [PIDNodeDraft(pid) for pid in create_pids(2, 'parent')]
    draft_pids = create_pids(2, 'draft')

    # create a parent-draft relationship
    parent_pids[0].insert_child(draft_pids[0])

    assert parent_pids[0].children.all() == [draft_pids[0]]

    # try to create invalid additional parent-draft relationships
    with pytest.raises(PIDRelationConsistencyError):
        parent_pids[0].insert_child(draft_pids[1])
        parent_pids[1].insert_child(draft_pids[0])
