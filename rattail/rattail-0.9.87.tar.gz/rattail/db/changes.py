# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2019 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Data Changes Interface
"""

from __future__ import unicode_literals, absolute_import

import logging

from packaging.version import parse as parse_version
import sqlalchemy as sa
from sqlalchemy.orm import object_mapper, RelationshipProperty
from sqlalchemy.orm.interfaces import SessionExtension
from sqlalchemy.orm.session import Session

try:
    from sqlalchemy.event import listen
except ImportError:
    listen = None # old SQLAlchemy; will have to work around that, below

from rattail.db import model
from rattail.core import get_uuid
from rattail.util import load_object

try:
    from rattail.db.continuum import versioning_manager
except ImportError:             # assume no continuum
    versioning_manager = None


log = logging.getLogger(__name__)


def record_changes(session, recorder=None, config=None):
    """
    Record all relevant data changes which occur within a session.

    :param session: A :class:`sqlalchemy:sqlalchemy.orm.session.Session` class,
       or instance thereof.
    """
    if isinstance(recorder, ChangeRecorder):
        pass
    elif callable(recorder):
        recorder = recorder()
    elif recorder is None:
        if config:
            spec = config.get('rattail.db', 'changes.recorder', usedb=False)
            if spec:
                recorder = load_object(spec)()
        if not recorder:
            recorder = ChangeRecorder()
    else:
        raise ValueError("Invalid 'recorder' parameter: {}".format(repr(recorder)))

    if listen:
        listen(session, 'before_flush', recorder)
    else:
        extension = ChangeRecorderExtension(recorder)
        if isinstance(session, Session):
            session.extensions.append(extension)
        else:
            session.configure(extension=extension)

    session.rattail_record_changes = True
    session.rattail_change_recorder = recorder


class ChangeRecorder(object):
    """
    Listener for session ``before_flush`` events.

    This class is responsible for adding stub records to the ``changes`` table,
    which will in turn be used by the database synchronizer to manage change
    data propagation.
    """
    ignored_classes = (
        model.Setting,
        model.Change,
        model.DataSyncChange,
    )

    # once upon a time we supposedly needed to specify `passive=True` when
    # invoking `session.is_modified()` but that has apparently been deprecated
    # for some time now.  we likely should just require SA>=0.8 instead of
    # maintaining this logic?
    is_modified_kw = {}
    if parse_version(sa.__version__) < parse_version('0.8'):
        is_modified_kw['passive'] = True

    def __call__(self, session, flush_context, instances):
        """
        Method invoked when session ``before_flush`` event occurs.
        """
        # TODO: what a mess, need to look into this again at some point...
        # # TODO: Not sure if our event replaces the one registered by Continuum,
        # # or what.  But this appears to be necessary to keep that system
        # # working when we enable ours...
        # if versioning_manager:
        #     versioning_manager.before_flush(session, flush_context, instances)

        for obj in session.deleted:
            if not self.ignore_object(obj):
                self.process_deleted_object(session, obj)
        for obj in session.new:
            if not self.ignore_object(obj):
                self.process_new_object(session, obj)
        for obj in session.dirty:
            if not self.ignore_object(obj) and session.is_modified(obj, **self.is_modified_kw):
                # Orphaned objects which really are pending deletion show up in
                # session.dirty instead of session.deleted, hence this check.
                # https://groups.google.com/d/msg/sqlalchemy/H4nQTHphc0M/Xr8-Cgra0Z4J
                if self.is_deletable_orphan(obj):
                    self.process_deleted_object(session, obj)
                else:
                    self.process_dirty_object(session, obj)

    def ignore_object(self, obj):
        """
        Return ``True`` if changes for the given object should be ignored.
        """
        # ignore certain classes per declaration
        if isinstance(obj, self.ignored_classes):
            return True

        # TODO: is there a smarter way to check?
        # definitely don't care about changes to any version tables
        if obj.__class__.__name__.endswith('Version'):
            return True

        # ignore LabelProfile objects which are *not* marked "sync me"
        if isinstance(obj, model.LabelProfile) and not obj.sync_me:
            return True

        return False # i.e. don't ignore

    def process_new_object(self, session, obj):
        """
        Record changes as appropriate, for the given 'new' object.
        """
        self.record_rattail_change(session, obj, type_='new')

    def process_dirty_object(self, session, obj):
        """
        Record changes as appropriate, for the given 'dirty' object.
        """
        self.record_rattail_change(session, obj, type_='dirty')

    def process_deleted_object(self, session, obj):
        """
        Record changes as appropriate, for the given 'deleted' object.
        """
        # TODO: Is this hacky?  Seems like maybe so...
        if isinstance(obj, (model.PersonEmailAddress, model.PersonPhoneNumber, model.PersonMailingAddress)):
            self.record_rattail_change(session, obj.person, type_='dirty')
        if isinstance(obj, (model.EmployeeStore, model.EmployeeDepartment)):
            self.record_rattail_change(session, obj.employee, type_='dirty')
        self.record_rattail_change(session, obj, type_='deleted')

    def is_deletable_orphan(self, instance):
        """
        Determine if an object is an orphan and pending deletion.
        """
        mapper = object_mapper(instance)
        for property_ in mapper.iterate_properties:
            if isinstance(property_, RelationshipProperty):
                relationship = property_

                # Does this relationship refer back to the instance class?
                backref = relationship.backref or relationship.back_populates
                if backref:

                    # Does the other class mapper's relationship wish to delete orphans?
                    # other_relationship = relationship.mapper.relationships[backref]

                    # Sometimes backrefs are tuples; first element is name.
                    if isinstance(backref, tuple):
                        backref = backref[0]

                    other_relationship = relationship.mapper.get_property(backref)
                    if other_relationship.cascade.delete_orphan:

                        # Is this instance an orphan?
                        if getattr(instance, relationship.key) is None:
                            return True

        return False

    def record_rattail_change(self, session, instance, type_='dirty'):
        """
        Record a change record in the database.

        If ``instance`` represents a change in which we are interested, then
        this method will create (or update) a :class:`rattail.db.model.Change`
        record.

        :returns: ``True`` if a change was recorded, or ``False`` if it was
           ignored.
        """
        # TODO: this check is now redundant due to `ignore_object()`
        # No need to record changes for changes.
        if isinstance(instance, (model.Change, model.DataSyncChange)):
            return False

        # No need to record changes for batch data.
        if isinstance(instance, (model.BatchMixin, model.BatchRowMixin)):
            return False

        # no need to record changes for email attempts
        if isinstance(instance, model.EmailAttempt):
            return False

        # Ignore instances which don't use UUID.
        if not hasattr(instance, 'uuid'):
            return False

        # Provide an UUID value, if necessary.
        self.ensure_uuid(instance)

        # Record the change.
        self.record_change(session, quiet=True,
                           class_name=instance.__class__.__name__,
                           instance_uuid=instance.uuid,
                           deleted=type_ == 'deleted')
        log.debug("recorded change for {} {} {}: {}".format(
            type_, instance.__class__.__name__, instance.uuid, instance))
        return True

    def record_change(self, session, quiet=False, **kwargs):
        """
        Record a change, by creating a new change record in the session.
        """
        session.add(model.Change(**kwargs))
        if not quiet:
            log.debug("recorded {} for {} with key: {}".format(
                'deletion' if kwargs.get('deleted') else 'change',
                kwargs.get('class_name'),
                kwargs.get('object_key', kwargs.get('instance_uuid'))))

    def ensure_uuid(self, instance):
        """
        Ensure the given instance has a UUID value.

        This uses the following logic:

        * If the instance already has a UUID, nothing will be done.

        * If the instance contains a foreign key to another table, then that
          relationship will be traversed and the foreign object's UUID will be used
          to populate that of the instance.

        * Otherwise, a new UUID will be generated for the instance.
        """

        if instance.uuid:
            return

        mapper = object_mapper(instance)
        if not mapper.columns['uuid'].foreign_keys:
            instance.uuid = get_uuid()
            return

        for prop in mapper.iterate_properties:
            if (isinstance(prop, RelationshipProperty)
                and len(prop.remote_side) == 1
                and list(prop.remote_side)[0].key == 'uuid'):

                foreign_instance = getattr(instance, prop.key)
                if foreign_instance:
                    self.ensure_uuid(foreign_instance)
                    instance.uuid = foreign_instance.uuid
                    return

        instance.uuid = get_uuid()
        log.error("unexpected scenario; generated new UUID for instance: {0}".format(repr(instance)))


class ChangeRecorderExtension(SessionExtension):
    """
    Session extension for recording changes.

    .. note::
       This is only used when the installed SQLAlchemy version is old enough
       not to support the new event interfaces.
    """

    def __init__(self, recorder):
        self.recorder = recorder

    def before_flush(self, session, flush_context, instances):
        self.recorder(session, flush_context, instances)
