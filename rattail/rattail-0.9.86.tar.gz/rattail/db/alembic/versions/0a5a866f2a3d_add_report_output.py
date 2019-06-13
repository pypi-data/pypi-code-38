# -*- coding: utf-8 -*-
"""add report_output

Revision ID: 0a5a866f2a3d
Revises: 6ef6db00abe8
Create Date: 2017-03-21 21:57:03.435177

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '0a5a866f2a3d'
down_revision = u'6ef6db00abe8'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # report_output
    op.create_table('report_output',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('created', sa.DateTime(), nullable=False),
                    sa.Column('created_by_uuid', sa.String(length=32), nullable=False),
                    sa.Column('record_count', sa.Integer(), nullable=True),
                    sa.Column('report_name', sa.String(length=255), nullable=True),
                    sa.Column('filename', sa.String(length=255), nullable=True),
                    sa.ForeignKeyConstraint(['created_by_uuid'], [u'user.uuid'], name=u'report_output_fk_created_by'),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():

    # report_output
    op.drop_table('report_output')
