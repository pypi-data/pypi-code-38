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
Data models for scheduled app upgrades
"""

from __future__ import unicode_literals, absolute_import

import datetime

import six
import sqlalchemy as sa
from sqlalchemy import orm

from rattail.db.model import Base, uuid_column, User


@six.python_2_unicode_compatible
class Upgrade(Base):
    """
    Represents a scheduled app upgrade.
    """
    __tablename__ = 'upgrade'
    __table_args__ = (
        sa.ForeignKeyConstraint(['created_by_uuid'], ['user.uuid'], name='upgrade_fk_created_by'),
        sa.ForeignKeyConstraint(['executed_by_uuid'], ['user.uuid'], name='upgrade_fk_executed_by'),
    )

    uuid = uuid_column()

    created = sa.Column(sa.DateTime(), nullable=True, default=datetime.datetime.utcnow, doc="""
    Date and time when the upgrade record was created.
    """)

    created_by_uuid = sa.Column(sa.String(length=32), nullable=False)
    created_by = orm.relationship(
        User,
        foreign_keys=[created_by_uuid],
        doc="""
        Reference to user who created the upgrade record.
        """)

    description = sa.Column(sa.String(length=255), nullable=False, doc="""
    Basic (identifying) description for the upgrade.
    """)

    not_until = sa.Column(sa.DateTime(), nullable=True, doc="""
    If this is null, upgrade may occur at any time.  Otherwise the upgrade
    should not occur until after this time.
    """)

    notes = sa.Column(sa.Text(), nullable=True, doc="""
    Generic notes for the upgrade.
    """)

    enabled = sa.Column(sa.Boolean(), nullable=False, default=False, doc="""
    Whether or not the upgrade should be allowed to occur at all.
    """)

    executing = sa.Column(sa.Boolean(), nullable=False, default=False, doc="""
    Whether or not the upgrade is currently being performed.
    """)

    status_code = sa.Column(sa.Integer(), nullable=True, doc="""
    Current status code for the upgrade.
    """)

    executed = sa.Column(sa.DateTime(), nullable=True, doc="""
    Date and time when the upgrade was performed.
    """)

    executed_by_uuid = sa.Column(sa.String(length=32), nullable=True)
    executed_by = orm.relationship(
        User,
        foreign_keys=[executed_by_uuid],
        doc="""
        Reference to user who performed the upgrade.
        """)

    exit_code = sa.Column(sa.Integer(), nullable=True, doc="""
    Exit code for the upgrade execution process, if applicable.
    """)

    def __str__(self):
        return str(self.description or "")


class UpgradeRequirement(Base):
    """
    A package version requirement for an app upgrade.
    """
    __tablename__ = 'upgrade_requirement'
    __table_args__ = (
        sa.ForeignKeyConstraint(['upgrade_uuid'], ['upgrade.uuid'], name='upgrade_requirement_fk_upgrade'),
    )

    uuid = uuid_column()

    upgrade_uuid = sa.Column(sa.String(length=32), nullable=False)
    upgrade = orm.relationship(
        Upgrade,
        backref=orm.backref(
            'requirements'))

    package = sa.Column(sa.String(length=255), nullable=False, doc="""
    Package name as found on PyPI (or at least interpretable by pip).
    """)

    version = sa.Column(sa.String(length=255), nullable=False, default='LATEST', doc="""
    Version requirement for the package.  If the value is ``'LATEST'`` then the
    latest available version will be installed; otherwise the value is applied
    as-is to the package when building the requirement string.
    """)
