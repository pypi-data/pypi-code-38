# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""api query tests."""

import pytest
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from sqlalchemy.orm import aliased

from invenio_pidrelations.api import PIDQuery
from invenio_pidrelations.models import PIDRelation


@pytest.mark.parametrize("order, sort", [
    # Test default value, i.e. "desc"
    ({}, lambda children: list(reversed(children))),
    ({'ord': 'asc'}, lambda children: children),
    ({'ord': 'desc'}, lambda children: list(reversed(children)))
])
def test_query_order(db, version_pids, order, sort):
    """Test PIDQuery.order()."""
    result = PIDQuery([PersistentIdentifier], db.session()).join(
        PIDRelation,
        PersistentIdentifier.id == PIDRelation.child_id
    ).filter(
        PIDRelation.parent_id == version_pids[0]['parent'].id
    ).ordered(**order).all()
    assert result == sort(version_pids[0]['children'])


@pytest.mark.parametrize("status, filt", [
    (
        # Test with a PIDStatus
        PIDStatus.REGISTERED,
        lambda children: [child for child in children if child.status in [
            PIDStatus.REGISTERED
        ]]
    ),
    (
        # Test with a list of PIDStatus
        [PIDStatus.REGISTERED, PIDStatus.DELETED],
        lambda children: [child for child in children if child.status in [
            PIDStatus.REGISTERED, PIDStatus.DELETED
        ]]
    ),
])
def test_query_status(db, version_pids, status, filt):
    """Test PIDQuery.status()."""
    # test with simple join
    result = PIDQuery([PersistentIdentifier], db.session()).join(
        PIDRelation,
        PersistentIdentifier.id == PIDRelation.child_id
    ).filter(
        PIDRelation.parent_id == version_pids[0]['parent'].id
    ).status(status).ordered('asc').all()
    assert result == filt(version_pids[0]['children'])

    # test with double join (parent and child PID)
    parent_pid = aliased(PersistentIdentifier, name='parent_pid')
    child_pid = aliased(PersistentIdentifier, name='child_pid')
    result2 = PIDQuery(
        [child_pid], db.session(), _filtered_pid_class=child_pid
    ).join(
        PIDRelation,
        child_pid.id == PIDRelation.child_id
    ).join(
        parent_pid,
        parent_pid.id == PIDRelation.parent_id
    ).filter(
        parent_pid.pid_value == version_pids[0]['parent'].pid_value
    ).status(status).ordered(ord='asc').all()
    assert result == filt(version_pids[0]['children'])
