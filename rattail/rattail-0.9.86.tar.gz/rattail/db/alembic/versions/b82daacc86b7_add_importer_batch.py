# -*- coding: utf-8; -*-
"""add importer batch

Revision ID: b82daacc86b7
Revises: a809caf23cf0
Create Date: 2017-12-29 00:16:43.897114

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'b82daacc86b7'
down_revision = u'0c91cf7d557b'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch_importer
    op.create_table('batch_importer',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('description', sa.String(length=255), nullable=True),
                    sa.Column('created', sa.DateTime(), nullable=False),
                    sa.Column('created_by_uuid', sa.String(length=32), nullable=False),
                    sa.Column('cognized', sa.DateTime(), nullable=True),
                    sa.Column('cognized_by_uuid', sa.String(length=32), nullable=True),
                    sa.Column('rowcount', sa.Integer(), nullable=True),
                    sa.Column('complete', sa.Boolean(), nullable=True),
                    sa.Column('executed', sa.DateTime(), nullable=True),
                    sa.Column('executed_by_uuid', sa.String(length=32), nullable=True),
                    sa.Column('purge', sa.Date(), nullable=True),
                    sa.Column('notes', sa.Text(), nullable=True),
                    sa.Column('status_code', sa.Integer(), nullable=True),
                    sa.Column('status_text', sa.String(length=255), nullable=True),
                    sa.Column('row_table', sa.String(length=255), nullable=False),
                    sa.Column('batch_handler_spec', sa.String(length=255), nullable=True),
                    sa.Column('import_handler_spec', sa.String(length=255), nullable=False),
                    sa.Column('host_title', sa.String(length=255), nullable=False),
                    sa.Column('local_title', sa.String(length=255), nullable=False),
                    sa.Column('importer_key', sa.String(length=100), nullable=False),
                    sa.ForeignKeyConstraint(['cognized_by_uuid'], [u'user.uuid'], name=u'batch_importer_fk_cognized_by'),
                    sa.ForeignKeyConstraint(['created_by_uuid'], [u'user.uuid'], name=u'batch_importer_fk_created_by'),
                    sa.ForeignKeyConstraint(['executed_by_uuid'], [u'user.uuid'], name=u'batch_importer_fk_executed_by'),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():

    # batch_importer
    op.drop_table('batch_importer')
