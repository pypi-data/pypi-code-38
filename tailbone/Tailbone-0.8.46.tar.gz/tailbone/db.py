# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
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
Database Stuff
"""

from __future__ import unicode_literals, absolute_import

import sqlalchemy as sa
from zope.sqlalchemy import datamanager
import sqlalchemy_continuum as continuum
from sqlalchemy.orm import sessionmaker, scoped_session

from rattail.db import SessionBase
from rattail.db.continuum import versioning_manager


Session = scoped_session(sessionmaker(class_=SessionBase, rattail_config=None, rattail_record_changes=False, expire_on_commit=False))

# not necessarily used, but here if you need it
TempmonSession = scoped_session(sessionmaker())
TrainwreckSession = scoped_session(sessionmaker())


class TailboneSessionDataManager(datamanager.SessionDataManager):
    """Integrate a top level sqlalchemy session transaction into a zope transaction

    One phase variant.

    .. note::
       This class appears to be necessary in order for the Continuum
       integration to work alongside the Zope transaction integration.
    """

    def tpc_vote(self, trans):
        # for a one phase data manager commit last in tpc_vote
        if self.tx is not None:  # there may have been no work to do

            # Force creation of Continuum versions for current session.
            uow = versioning_manager.unit_of_work(self.session)
            uow.make_versions(self.session)

            self.tx.commit()
            self._finish('committed')


def join_transaction(session, initial_state=datamanager.STATUS_ACTIVE, transaction_manager=datamanager.zope_transaction.manager, keep_session=False):
    """Join a session to a transaction using the appropriate datamanager.

    It is safe to call this multiple times, if the session is already joined
    then it just returns.

    `initial_state` is either STATUS_ACTIVE, STATUS_INVALIDATED or STATUS_READONLY

    If using the default initial status of STATUS_ACTIVE, you must ensure that
    mark_changed(session) is called when data is written to the database.

    The ZopeTransactionExtesion SessionExtension can be used to ensure that this is
    called automatically after session write operations.

    .. note::
       This function is copied from upstream, and tweaked so that our custom
       :class:`TailboneSessionDataManager` will be used.
    """
    if datamanager._SESSION_STATE.get(id(session), None) is None:
        if session.twophase:
            DataManager = datamanager.TwoPhaseSessionDataManager
        else:
            DataManager = TailboneSessionDataManager
        DataManager(session, initial_state, transaction_manager, keep_session=keep_session)


class ZopeTransactionExtension(datamanager.ZopeTransactionExtension):
    """Record that a flush has occurred on a session's connection. This allows
    the DataManager to rollback rather than commit on read only transactions.

    .. note::
       This class is copied from upstream, and tweaked so that our custom
       :func:`join_transaction()` will be used.
    """

    def after_begin(self, session, transaction, connection):
        join_transaction(session, self.initial_state, self.transaction_manager, self.keep_session)

    def after_attach(self, session, instance):
        join_transaction(session, self.initial_state, self.transaction_manager, self.keep_session)


def register(session, initial_state=datamanager.STATUS_ACTIVE,
             transaction_manager=datamanager.zope_transaction.manager, keep_session=False):
    """Register ZopeTransaction listener events on the
    given Session or Session factory/class.

    This function requires at least SQLAlchemy 0.7 and makes use
    of the newer sqlalchemy.event package in order to register event listeners
    on the given Session.

    The session argument here may be a Session class or subclass, a
    sessionmaker or scoped_session instance, or a specific Session instance.
    Event listening will be specific to the scope of the type of argument
    passed, including specificity to its subclass as well as its identity.

    .. note::
       This function is copied from upstream, and tweaked so that our custom
       :class:`ZopeTransactionExtension` will be used.
    """
    from sqlalchemy import event

    ext = ZopeTransactionExtension(
        initial_state=initial_state,         
        transaction_manager=transaction_manager,
        keep_session=keep_session,
    )

    event.listen(session, "after_begin", ext.after_begin)
    event.listen(session, "after_attach", ext.after_attach)
    event.listen(session, "after_flush", ext.after_flush)
    event.listen(session, "after_bulk_update", ext.after_bulk_update)
    event.listen(session, "after_bulk_delete", ext.after_bulk_delete)
    event.listen(session, "before_commit", ext.before_commit)


register(Session)
register(TempmonSession)
register(TrainwreckSession)
