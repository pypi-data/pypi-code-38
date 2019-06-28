# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""API for PID relations concepts."""

from __future__ import absolute_import, print_function

from flask import Blueprint
from invenio_db import db
from invenio_pidstore.models import PIDStatus

from invenio_pidrelations.contrib.draft import PIDNodeDraft

from ..api import PIDNodeOrdered
from ..errors import PIDRelationConsistencyError
from ..utils import resolve_relation_type_config


class PIDNodeVersioning(PIDNodeOrdered):
    """API for PID versioning relations.

    parents (max: 1): a PID linked to all the versions of a record
                      and always redirecting to its last version.
    children (max: unlimited): PIDs of the different versions of a record.

    Children PIDs are separated in two categories: RESERVED and REGISTERED.

    There can be only one RESERVED PID. It is considered as the "draft" PID,
    i.e. the next version to publish. This draft/RESERVED PID is the parent PID
    of a "deposit" PID (see invenio-deposit). The PIDNodeDraft API is used in
    order to manipulate the relation between the draft PID and its child
    deposit PID.

    REGISTERED PIDs are published record PIDs which each represents a
    version of the original record.

    The parent PID's status is RESERVED as long as no Version is published,
    i.e. REGISTERED.
    """

    def __init__(self, pid):
        """Create a PID versioning API.

        :param pid: either the parent PID or a specific record version PID.
        """
        self.relation_type = resolve_relation_type_config('version')
        super(PIDNodeVersioning, self).__init__(
            pid=pid, relation_type=self.relation_type,
            max_parents=1, max_children=None
        )

    @property
    def children(self):
        """Children of the parent."""
        return super(PIDNodeVersioning, self).\
            children.status(PIDStatus.REGISTERED)

    def insert_child(self, child_pid, index=-1):
        """Insert a Version child PID."""
        if child_pid.status != PIDStatus.REGISTERED:
            raise PIDRelationConsistencyError(
                "Version PIDs should have status 'REGISTERED'. Use "
                "insert_draft_child to insert 'RESERVED' draft PID.")
        with db.session.begin_nested():
            # if there is a draft and "child" is inserted as the last version,
            # it should be inserted before the draft.
            draft = self.draft_child
            if draft and index == -1:
                index = self.index(draft)
            super(PIDNodeVersioning, self).insert_child(child_pid, index=index)
            self.update_redirect()

    def remove_child(self, child_pid):
        """Remove a Version child PID.

        Extends the base method call by redirecting from the parent to the
        last child.
        """
        if child_pid.status == PIDStatus.RESERVED:
            raise PIDRelationConsistencyError(
                "Version PIDs should not have status 'RESERVED'. Use "
                "remove_draft_child to remove a draft PID.")
        with db.session.begin_nested():
            super(PIDNodeVersioning, self).remove_child(child_pid,
                                                        reorder=True)
            self.update_redirect()

    @property
    def draft_child(self):
        """Get the draft (RESERVED) child."""
        return super(PIDNodeVersioning, self).children.status(
            PIDStatus.RESERVED
        ).one_or_none()

    @property
    def draft_child_deposit(self):
        """Get the deposit PID of the draft child.

        Return `None` if no draft child PID exists.
        """
        if self.draft_child:
            return PIDNodeDraft(self.draft_child).children.one_or_none()
        else:
            return None

    def insert_draft_child(self, child_pid):
        """Insert a draft child to versioning."""
        if child_pid.status != PIDStatus.RESERVED:
            raise PIDRelationConsistencyError(
                "Draft child should have status 'RESERVED'")

        if not self.draft_child:
            with db.session.begin_nested():
                super(PIDNodeVersioning, self).insert_child(child_pid,
                                                            index=-1)
        else:
            raise PIDRelationConsistencyError(
                "Draft child already exists for this relation: {0}".format(
                    self.draft_child))

    def remove_draft_child(self):
        """Remove the draft child from versioning."""
        if self.draft_child:
            with db.session.begin_nested():
                super(PIDNodeVersioning, self).remove_child(self.draft_child,
                                                            reorder=True)

    def update_redirect(self):
        """Update the parent redirect to the current last child.

        This method should be called on the parent PID node.

        Use this method when the status of a PID changed (ex: draft changed
        from RESERVED to REGISTERED)
        """
        if self.last_child:
            self._resolved_pid.redirect(self.last_child)
        elif any(map(lambda pid: pid.status not in [PIDStatus.DELETED,
                                                    PIDStatus.REGISTERED,
                                                    PIDStatus.RESERVED],
                     super(PIDNodeVersioning, self).children.all())):
            raise PIDRelationConsistencyError(
                "Invalid relation state. Only REGISTERED, RESERVED "
                "and DELETED PIDs are supported."
            )


versioning_blueprint = Blueprint(
    'invenio_pidrelations.versioning',
    __name__,
    template_folder='templates'
)


@versioning_blueprint.app_template_filter()
def to_versioning_api(pid):
    """Get PIDNodeVersioning object."""
    return PIDNodeVersioning(pid=pid)


__all__ = (
    'PIDNodeVersioning',
    'versioning_blueprint'
)
