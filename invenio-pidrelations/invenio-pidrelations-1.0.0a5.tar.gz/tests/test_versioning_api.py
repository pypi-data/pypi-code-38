# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

from __future__ import absolute_import, print_function

import pytest
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from test_helpers import create_pids, filter_pids, with_pid_and_fetched_pid

from invenio_pidrelations.contrib.versioning import PIDNodeVersioning
from invenio_pidrelations.errors import PIDRelationConsistencyError


@with_pid_and_fetched_pid
def test_versioning_children(db, version_pids, build_pid):
    """Test the children property of PIDNoneVersioning."""
    parent_pid = build_pid(version_pids[0]['parent'])
    h1 = PIDNodeVersioning(parent_pid)
    assert h1.children.ordered('asc').all() == \
        filter_pids(version_pids[0]['children'], PIDStatus.REGISTERED)


@with_pid_and_fetched_pid
def test_versioning_insert_child(db, version_pids, build_pid):
    """Test PIDNodeVersioning.insert_child(...)."""
    new_pids = create_pids(3)
    parent_pid = build_pid(version_pids[0]['parent'])
    h1 = PIDNodeVersioning(parent_pid)
    # insert as first child
    h1.insert_child(new_pids[0], 0)
    version_pids[0]['children'].insert(0, new_pids[0])
    assert h1.children.ordered('asc').all() == \
        filter_pids(version_pids[0]['children'], PIDStatus.REGISTERED)

    # insert as last child. This should insert just before the draft
    version_pids[0]['children'].insert(h1.index(h1.draft_child), new_pids[1])
    h1.insert_child(new_pids[1], -1)
    # Check that the parent redirects to the added PID
    assert(version_pids[0]['parent'].get_redirect() == new_pids[1])
    # Register the draft so that it appears in the children
    h1.draft_child.register()
    h1.update_redirect()
    assert h1.children.ordered('asc').all() == \
        filter_pids(version_pids[0]['children'], PIDStatus.REGISTERED)

    # insert again but without a draft child. It should be inserted at the end.
    version_pids[0]['children'].append(new_pids[2])
    h1.insert_child(new_pids[2], -1)
    assert h1.children.ordered('asc').all() == \
        filter_pids(version_pids[0]['children'], PIDStatus.REGISTERED)

    reserved_pid = create_pids(1, status=PIDStatus.RESERVED)[0]

    # Check the exception raised when trying to insert a RESERVED PID
    with pytest.raises(PIDRelationConsistencyError):
        h1.insert_child(reserved_pid)


@with_pid_and_fetched_pid
def test_versioning_remove_child(db, version_pids, build_pid):
    """Test the remove child method of PIDNodeVersioning."""
    parent_pid = build_pid(version_pids[0]['parent'])
    h1 = PIDNodeVersioning(parent_pid)
    # try to remove the draft child using remove_child
    with pytest.raises(PIDRelationConsistencyError):
        h1.remove_child(version_pids[0]['children'][-1])
    # assert that the parent redirects to the last child
    assert version_pids[0]['parent'].get_redirect() == \
        version_pids[0]['children'][2]
    # remove the last child
    h1.remove_child(version_pids[0]['children'][2])
    # assert that the pid is not a child
    assert version_pids[0]['children'][2] not in h1.children.all()
    # assert that the parent now redirects to the new last child
    assert version_pids[0]['parent'].get_redirect() == \
        version_pids[0]['children'][1]

    # test removing the first child doesn't change the redirect
    h1.remove_child(version_pids[0]['children'][0])
    assert version_pids[0]['parent'].get_redirect() == \
        version_pids[0]['children'][1]


@with_pid_and_fetched_pid
def test_versioning_insert_draft_child(db, version_pids, build_pid):
    """Test the insert_draft_child method of PIDNodeVersioning."""
    parent_pid = build_pid(version_pids[0]['parent'])
    h1 = PIDNodeVersioning(parent_pid)
    # assert that there is a draft_child present
    assert h1.draft_child == version_pids[0]['children'][-1]
    draft2 = PersistentIdentifier.create('recid', 'foobar.draft2',
                                         object_type='rec',
                                         status=PIDStatus.RESERVED)
    with pytest.raises(PIDRelationConsistencyError):
        # try to add a second draft_child
        h1.insert_draft_child(draft2)


@with_pid_and_fetched_pid
def test_versioning_remove_draft_child(db, version_pids, build_pid):
    """Test the remove_draft_child method of PIDNodeVersioning."""
    parent_pid = build_pid(version_pids[0]['parent'])
    h1 = PIDNodeVersioning(parent_pid)
    h1.remove_draft_child()
    assert h1.draft_child is None


@with_pid_and_fetched_pid
def test_versioning_draft_child_deposit(db, version_pids, build_pid):
    """Test the draft_child_deposit property of PIDNodeVersioning."""
    parent_pid = build_pid(version_pids[0]['parent'])
    h1 = PIDNodeVersioning(parent_pid)
    assert h1.draft_child_deposit == version_pids[0]['deposit']


@with_pid_and_fetched_pid
def test_update_redirect(db, version_pids, build_pid):
    """Test PIDNodeVersioning.update_redirect()."""
    # Test update_redirect on a PID without any child
    parent_pids = create_pids(1, prefix='parent', status=PIDStatus.RESERVED)
    draft_pids = create_pids(2, prefix='draft', status=PIDStatus.RESERVED)
    parent = PIDNodeVersioning(build_pid(parent_pids[0]))
    parent.update_redirect()
    assert parent_pids[0].status == PIDStatus.RESERVED

    # Test that update_redirect remains reserved once it has a draft child
    parent.insert_draft_child(draft_pids[0])
    assert parent_pids[0].status == PIDStatus.RESERVED

    h1 = PIDNodeVersioning(build_pid(version_pids[0]['parent']))

    def test_redirect(expected_length, expected_redirect):
        filtered = filter_pids(version_pids[0]['children'],
                               status=PIDStatus.REGISTERED)
        assert len(filtered) == expected_length
        assert h1.children.ordered('asc').all() == filtered
        assert h1._resolved_pid.get_redirect() == expected_redirect

    # Test update_redirect when it already points to the last version
    last = h1.last_child
    draft = h1.draft_child
    h1.update_redirect()
    test_redirect(3, last)

    # Test update_redirect after publishing the draft
    h1.draft_child.register()
    h1.update_redirect()
    test_redirect(4, draft)

    # Test update_redirect after deleting the last version
    h1.last_child.delete()
    h1.update_redirect()
    test_redirect(3, last)

    # Test that if every version is deleted the HEAD pid is also deleted
    for pid in filter_pids(version_pids[0]['children'],
                           status=PIDStatus.REGISTERED):
        pid.delete()
    h1.update_redirect()
    test_redirect(0, last)

    # Test that an exception is raised if unsupported PIDStatus are used.
    version_pids[0]['children'][0].status = PIDStatus.NEW
    with pytest.raises(PIDRelationConsistencyError):
        h1.update_redirect()
