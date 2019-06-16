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
Models for generic data export history
"""

from __future__ import unicode_literals, absolute_import

import datetime

import six
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declared_attr

from rattail.db.model import uuid_column, User


@six.python_2_unicode_compatible
class ExportMixin(object):
    """
    Mixin for all generic export models
    """

    @declared_attr
    def __table_args__(cls):
        return cls.__default_table_args__()

    @classmethod
    def __default_table_args__(cls):
        return cls.__export_table_args__()

    @classmethod
    def __export_table_args__(cls):
        return (
            sa.ForeignKeyConstraint(['created_by_uuid'], ['user.uuid'],
                                    name='{}_fk_created_by'.format(cls.__tablename__)),
        )

    @declared_attr
    def export_key(cls):
        return cls.__tablename__

    uuid = uuid_column()

    id = sa.Column(sa.Integer(), sa.Sequence('batch_id_seq'), nullable=False, doc="""
    Unique ID number for the export.
    """)

    created = sa.Column(sa.DateTime(), nullable=False, default=datetime.datetime.utcnow, doc="""
    Date and time when the product export was created.
    """)

    created_by_uuid = sa.Column(sa.String(length=32), nullable=False)

    @declared_attr
    def created_by(cls):
        return orm.relationship(
            User,
            doc="""
            Reference to the user who created the export.
            """)
    
    record_count = sa.Column(sa.Integer(), nullable=True, doc="""
    Number of records included in the export.  This is a cached value,
    hopefully set at the time the export is generated.
    """)

    def __str__(self):
        return self.id_str

    @property
    def id_str(self):
        if self.id:
            return '{:08d}'.format(self.id)
        return 'pending'

    def filepath(self, config, filename=None, makedirs=False):
        """
        Returns absolute path to export's data folder, optionally appended with
        given filename.  This is a convenience method which really just invokes
        :meth:`rattail.config.RattailConfig.export_filepath()`.
        """
        return config.export_filepath(self.export_key, self.uuid,
                                      filename=filename, makedirs=makedirs)
