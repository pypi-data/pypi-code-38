# -*- coding: utf-8; -*-
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
SQLAlchemy-Continuum integration
"""

from __future__ import unicode_literals, absolute_import

import socket
import logging

import six

import sqlalchemy as sa
import sqlalchemy_continuum as continuum
from sqlalchemy_continuum.plugins import Plugin
from sqlalchemy_utils.functions import get_primary_keys

from rattail.util import OrderedDict

# TODO: Deprecate/remove this import.
from rattail.db.config import configure_versioning


log = logging.getLogger(__name__)


class RattailPlugin(Plugin):

    def transaction_args(self, uow, session):
        user = getattr(session, 'continuum_user', None)
        host = socket.gethostname()
        ip = socket.gethostbyname(host)
        return {
            'user_id': user.uuid if user else None,
            'remote_addr': ip,
        }


# TODO: we maybe should stop keeping our own reference to this?
# (it used to be "necessary" for customization, not it matters now)
versioning_manager = continuum.versioning_manager


def disable_versioning(manager=None):
    """
    Disable Continuum versioning.
    """
    log.info("disabling Continuum versioning")
    if manager is None:
        manager = versioning_manager
    continuum.remove_versioning(manager=manager)


def count_versions(obj):
    """
    Return the number of versions given object has.

    .. note::
       This function was copied from the one at
       :func:`continuum:sqlalchemy_continuum.utils.count_versions()`, and
       changed so as not to try to use the ``repr()`` value of the table's
       primary key value, since for us that's usually an UUID as unicode string.

    :param obj: SQLAlchemy declarative model object
    """
    session = sa.orm.object_session(obj)
    if session is None:
        # If object is transient, we assume it has no version history.
        return 0
    manager = continuum.get_versioning_manager(obj)
    table_name = manager.option(obj, 'table_name') % obj.__table__.name

    def value(o, k):
        v = getattr(o, k)
        if isinstance(v, six.text_type):
            v = v.encode('utf_8')
        return v

    criteria = [
        '%s = %r' % (pk, value(obj, pk))
        for pk in get_primary_keys(obj)
    ]
    query = 'SELECT COUNT(1) FROM %s WHERE %s' % (
        table_name,
        ' AND '.join(criteria)
    )
    return session.execute(query).scalar()


def model_transaction_query(session, instance, parent_class, child_classes=[]):
    """
    Return a query capable of finding all Continuum ``Transaction`` instances
    which are associated with a model instance.
    """
    from rattail.db import model

    Transaction = continuum.transaction_class(parent_class)
    Version = continuum.version_class(parent_class)

    query = session.query(Transaction)\
        .outerjoin(Version, sa.and_(
            Version.uuid == instance.uuid,
            Version.transaction_id == Transaction.id))

    classes = [Version]
    for model_class, foreign_attr, primary_attr in child_classes:
        cls = continuum.version_class(model_class)
        query = query.outerjoin(cls, sa.and_(
                cls.transaction_id == Transaction.id,
                getattr(cls, foreign_attr) == getattr(instance, primary_attr)))
        classes.append(cls)

    return query.filter(sa.or_(
            *[cls.uuid != None for cls in classes]))
