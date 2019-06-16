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
Data models for tempmon
"""

from __future__ import unicode_literals, absolute_import

import datetime

import six
import sqlalchemy as sa
from sqlalchemy import orm

from rattail.db.model import Base, uuid_column


@six.python_2_unicode_compatible
class TempmonClient(Base):
    """
    Represents a tempmon client.
    """
    __tablename__ = 'tempmon_client'
    __table_args__ = (
        sa.UniqueConstraint('config_key', name='tempmon_client_uq_config_key'),
    )
    model_title = "TempMon Client"

    uuid = uuid_column()
    config_key = sa.Column(sa.String(length=50), nullable=False)
    hostname = sa.Column(sa.String(length=255), nullable=False)
    location = sa.Column(sa.String(length=255), nullable=True)
    enabled = sa.Column(sa.Boolean(), nullable=False, default=False)
    online = sa.Column(sa.Boolean(), nullable=False, default=False)

    def __str__(self):
        return '{} ({})'.format(self.config_key, self.hostname)

    def enabled_probes(self):
        return [probe for probe in self.probes if probe.enabled]


@six.python_2_unicode_compatible
class TempmonProbe(Base):
    """
    Represents a probe connected to a tempmon client.
    """
    __tablename__ = 'tempmon_probe'
    __table_args__ = (
        sa.ForeignKeyConstraint(['client_uuid'], ['tempmon_client.uuid'], name='tempmon_probe_fk_client'),
        sa.UniqueConstraint('config_key', name='tempmon_probe_uq_config_key'),
    )
    model_title = "TempMon Probe"

    uuid = uuid_column()
    client_uuid = sa.Column(sa.String(length=32), nullable=False)

    client = orm.relationship(
        TempmonClient,
        doc="""
        Reference to the tempmon client to which this probe is connected.
        """,
        backref=orm.backref(
            'probes',
            doc="""
            List of probes connected to this client.
            """))

    config_key = sa.Column(sa.String(length=50), nullable=False)
    appliance_type = sa.Column(sa.Integer(), nullable=False)
    description = sa.Column(sa.String(length=255), nullable=False)
    device_path = sa.Column(sa.String(length=255), nullable=True)
    enabled = sa.Column(sa.Boolean(), nullable=False, default=True)

    good_temp_min = sa.Column(sa.Integer(), nullable=False)
    good_temp_max = sa.Column(sa.Integer(), nullable=False)
    critical_temp_min = sa.Column(sa.Integer(), nullable=False)
    critical_temp_max = sa.Column(sa.Integer(), nullable=False)
    therm_status_timeout = sa.Column(sa.Integer(), nullable=False)
    status_alert_timeout = sa.Column(sa.Integer(), nullable=False)

    status = sa.Column(sa.Integer(), nullable=True)
    status_changed = sa.Column(sa.DateTime(), nullable=True)
    status_alert_sent = sa.Column(sa.DateTime(), nullable=True)

    def __str__(self):
        return str(self.description or '')


@six.python_2_unicode_compatible
class TempmonReading(Base):
    """
    Represents a single tempurate reading from a tempmon probe.
    """
    __tablename__ = 'tempmon_reading'
    __table_args__ = (
        sa.ForeignKeyConstraint(['client_uuid'], ['tempmon_client.uuid'], name='tempmon_reading_fk_client'),
        sa.ForeignKeyConstraint(['probe_uuid'], ['tempmon_probe.uuid'], name='tempmon_reading_fk_probe'),
    )
    model_title = "TempMon Reading"

    uuid = uuid_column()

    client_uuid = sa.Column(sa.String(length=32), nullable=False)
    client = orm.relationship(
        TempmonClient,
        doc="""
        Reference to the tempmon client which took this reading.
        """)

    probe_uuid = sa.Column(sa.String(length=32), nullable=False)
    probe = orm.relationship(
        TempmonProbe,
        doc="""
        Reference to the tempmon probe which took this reading.
        """)

    taken = sa.Column(sa.DateTime(), nullable=False, default=datetime.datetime.utcnow)
    degrees_f = sa.Column(sa.Numeric(precision=7, scale=4), nullable=False)

    def __str__(self):
        return str(self.degrees_f)
