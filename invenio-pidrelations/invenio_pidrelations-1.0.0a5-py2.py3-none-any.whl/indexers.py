# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""PID relations indexers."""

from __future__ import absolute_import, print_function

from invenio_indexer.api import RecordIndexer
from invenio_pidstore.models import PersistentIdentifier
from invenio_records.api import Record

from .contrib.versioning import PIDNodeVersioning
from .serializers.utils import serialize_relations


def index_relations(sender, pid_type, json=None,
                    record=None, index=None, **kwargs):
    """Add relations to the indexed record."""
    if not json:
        json = {}
    pid = PersistentIdentifier.query.filter(
        PersistentIdentifier.object_uuid == record.id,
        PersistentIdentifier.pid_type == pid_type,
    ).one_or_none()
    relations = None
    if pid:
        relations = serialize_relations(pid)
        if relations:
            json['relations'] = relations
    return json


def index_siblings(pid, include_pid=False, children=None,
                   neighbors_eager=False, eager=False, with_deposits=True):
    """Send sibling records of the passed pid for indexing.

    Note: By default does not index the 'pid' itself,
          only zero or more siblings.

    :param pid: PID (recid) of whose siblings are to be indexed.
    :param children: Overrides children with a fixed list of PID.
        Children should contain the 'pid' itself if 'neighbors_eager' is to
        be used, otherwise the last child is treated as the only neighbor.
    :param eager: Index all siblings immediately.
    :param include_pid: If True, will index also the provided 'pid'
           (default:False).
    :param neighbors_eager: Index the neighboring PIDs w.r.t. 'pid'
        immediately, and the rest with a bulk_index (default: False)
    :param with_deposits: Reindex also corresponding record's deposits.
    """
    assert not (neighbors_eager and eager), \
        """Only one of the 'eager' and 'neighbors_eager' flags
        can be set to True, not both"""
    if children is None:
        parent_pid = PIDNodeVersioning(pid=pid).parents.first()
        children = PIDNodeVersioning(pid=parent_pid).children.all()
    objid = str(pid.object_uuid)
    children = [str(p.object_uuid) for p in children]

    idx = children.index(objid) if objid in children else len(children)

    # Split children (which can include the pid) into left and right siblings
    # If 'pid' is not in children, idx is the length of list, so 'left'
    # will be all children, and 'right' will be an empty list
    # [X X X] X [X X X]

    if include_pid:
        # [X X X X] [X X X]  Includes pid to the 'left' set
        left = children[:idx + 1]
    else:
        # [X X X] X [X X X]
        left = children[:idx]
    right = children[idx + 1:]

    if eager:
        eager_uuids = left + right
        bulk_uuids = []
    elif neighbors_eager:
        # neighbors are last of 'left' and first or 'right' siblings
        # X X [X] X [X] X X
        eager_uuids = left[-1:] + right[:1]
        # all of the siblings, except the neighbours
        # [X X] X X X [X X]
        bulk_uuids = left[:-1] + right[1:]
    else:
        eager_uuids = []
        bulk_uuids = left + right

    def get_dep_uuids(rec_uuids):
        """Get corresponding deposit UUIDs from record's UUIDs."""
        return [str(PersistentIdentifier.get(
                    'depid',
                    Record.get_record(id_)['_deposit']['id']).object_uuid)
                for id_ in rec_uuids]

    if with_deposits:
        eager_uuids += get_dep_uuids(eager_uuids)
        bulk_uuids += get_dep_uuids(bulk_uuids)

    for id_ in eager_uuids:
        RecordIndexer().index_by_id(id_)
    if bulk_uuids:
        RecordIndexer().bulk_index(bulk_uuids)
