# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2018 Lance Edgar
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
Data Models for DataSync Daemon
"""

from __future__ import unicode_literals

import datetime

import six
import sqlalchemy as sa

from rattail.db.model import Base, uuid_column


@six.python_2_unicode_compatible
class DataSyncChange(Base):
    """
    Represents a change obtained from a DataSync watcher thread, and destined
    for one or more DataSync consumers.
    """
    __tablename__ = 'datasync_change'
    model_title = "DataSync Change"

    uuid = uuid_column()

    source = sa.Column(sa.String(length=50), nullable=False, doc="""
    Key of the watcher from which this change was obtained.
    """)

    payload_type = sa.Column(sa.String(length=40), nullable=False, doc="""
    The "type" of payload represented by the change, e.g. 'Person'.  The
    :attr:`payload_key` should be unique for a given payload type.
    """)

    payload_key = sa.Column(sa.String(length=255), nullable=False, doc="""
    Key for the payload (presumably unique when combined with
    :attr:`payload_type`) represented by the change, within the watched
    database.
    """)

    deletion = sa.Column(sa.Boolean(), nullable=False, default=False, doc="""
    Whether the change represents a deletion; defaults to ``False``.
    """)

    obtained = sa.Column(sa.DateTime(), nullable=False, default=datetime.datetime.utcnow, doc="""
    Date and time when the change was obtained from the watcher thread.
    """)

    consumer = sa.Column(sa.String(length=50), nullable=True, doc="""
    Configured key of the DataSync consumer for which this change is destined.
    This may be NULL, in which case the change will go to all consumers
    configured as not "isolated".
    """)

    def __str__(self):
        if self.payload_type and self.payload_key:
            return "{}: {}{}".format(
                self.payload_type,
                self.payload_key,
                " (deletion)" if self.deletion else "")
        return "(empty)"
