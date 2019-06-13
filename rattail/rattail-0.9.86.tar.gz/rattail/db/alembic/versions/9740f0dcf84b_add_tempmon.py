# -*- coding: utf-8 -*-
"""add tempmon

Revision ID: 9740f0dcf84b
Revises: 3f266c89a3d4
Create Date: 2016-11-21 20:26:08.789247

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '9740f0dcf84b'
down_revision = u'3f266c89a3d4'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


batch_id_seq = sa.Sequence('batch_id_seq')


def upgrade():

    # tempmon_client
    op.create_table('tempmon_client',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('config_key', sa.String(length=50), nullable=False),
                    sa.Column('hostname', sa.String(length=255), nullable=False),
                    sa.Column('location', sa.String(length=255), nullable=True),
                    sa.Column('enabled', sa.Boolean(), nullable=False),
                    sa.Column('online', sa.Boolean(), nullable=False),
                    sa.UniqueConstraint('config_key', name='tempmon_client_uq_config_key'),
                    sa.PrimaryKeyConstraint('uuid')
    )

    # tempmon_probe
    op.create_table('tempmon_probe',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('client_uuid', sa.String(length=32), nullable=False),
                    sa.Column('config_key', sa.String(length=50), nullable=False),
                    sa.Column('appliance_type', sa.Integer(), nullable=False),
                    sa.Column('description', sa.String(length=255), nullable=False),
                    sa.Column('device_path', sa.String(length=255), nullable=True),
                    sa.Column('good_temp_min', sa.Integer(), nullable=False),
                    sa.Column('good_temp_max', sa.Integer(), nullable=False),
                    sa.Column('critical_temp_min', sa.Integer(), nullable=False),
                    sa.Column('critical_temp_max', sa.Integer(), nullable=False),
                    sa.Column('status_alert_timeout', sa.Integer(), nullable=False),
                    sa.Column('therm_status_timeout', sa.Integer(), nullable=False),
                    sa.Column('enabled', sa.Boolean(), nullable=False),
                    sa.Column('status', sa.Integer(), nullable=True),
                    sa.Column('status_changed', sa.DateTime(), nullable=True),
                    sa.Column('status_alert_sent', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['client_uuid'], [u'tempmon_client.uuid'], name=u'tempmon_probe_fk_client'),
                    sa.UniqueConstraint('config_key', name='tempmon_probe_uq_config_key'),
                    sa.PrimaryKeyConstraint('uuid')
    )

    # tempmon_reading
    op.create_table('tempmon_reading',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('client_uuid', sa.String(length=32), nullable=False),
                    sa.Column('probe_uuid', sa.String(length=32), nullable=False),
                    sa.Column('taken', sa.DateTime(), nullable=False),
                    sa.Column('degrees_f', sa.Numeric(precision=7, scale=4), nullable=False),
                    sa.ForeignKeyConstraint(['client_uuid'], [u'tempmon_client.uuid'], name=u'tempmon_reading_fk_client'),
                    sa.ForeignKeyConstraint(['probe_uuid'], [u'tempmon_probe.uuid'], name=u'tempmon_reading_fk_probe'),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():

    # tempmon
    op.drop_table('tempmon_reading')
    op.drop_table('tempmon_probe')
    op.drop_table('tempmon_client')
