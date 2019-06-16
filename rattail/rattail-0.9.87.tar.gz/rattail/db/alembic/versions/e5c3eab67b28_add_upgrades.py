# -*- coding: utf-8 -*-
"""add upgrades

Revision ID: e5c3eab67b28
Revises: 1242c7a0e24a
Create Date: 2017-08-05 16:30:36.615368

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'e5c3eab67b28'
down_revision = u'1242c7a0e24a'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # upgrade
    op.create_table('upgrade',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('created', sa.DateTime(), nullable=True),
                    sa.Column('created_by_uuid', sa.String(length=32), nullable=False),
                    sa.Column('description', sa.String(length=255), nullable=False),
                    sa.Column('not_until', sa.DateTime(), nullable=True),
                    sa.Column('notes', sa.Text(), nullable=True),
                    sa.Column('enabled', sa.Boolean(), nullable=False),
                    sa.Column('executing', sa.Boolean(), nullable=False),
                    sa.Column('executed', sa.DateTime(), nullable=True),
                    sa.Column('executed_by_uuid', sa.String(length=32), nullable=True),
                    sa.ForeignKeyConstraint(['created_by_uuid'], [u'user.uuid'], name=u'upgrade_fk_created_by'),
                    sa.ForeignKeyConstraint(['executed_by_uuid'], [u'user.uuid'], name=u'upgrade_fk_executed_by'),
                    sa.PrimaryKeyConstraint('uuid')
    )

    # upgrade_requirement
    op.create_table('upgrade_requirement',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('upgrade_uuid', sa.String(length=32), nullable=False),
                    sa.Column('package', sa.String(length=255), nullable=False),
                    sa.Column('version', sa.String(length=255), nullable=False),
                    sa.ForeignKeyConstraint(['upgrade_uuid'], [u'upgrade.uuid'], name=u'upgrade_requirement_fk_upgrade'),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():

    # upgrade*
    op.drop_table('upgrade_requirement')
    op.drop_table('upgrade')
