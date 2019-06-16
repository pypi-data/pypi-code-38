# -*- coding: utf-8 -*-
"""add person notes

Revision ID: 23600f00cda7
Revises: 7f88949a7ab9
Create Date: 2017-10-17 12:13:12.135529

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '23600f00cda7'
down_revision = u'7f88949a7ab9'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # note
    op.create_table('note',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('parent_type', sa.String(length=20), nullable=False),
                    sa.Column('parent_uuid', sa.String(length=32), nullable=False),
                    sa.Column('type', sa.String(length=15), nullable=True),
                    sa.Column('subject', sa.String(length=255), nullable=True),
                    sa.Column('text', sa.Text(), nullable=False),
                    sa.Column('created', sa.DateTime(), nullable=False),
                    sa.Column('created_by_uuid', sa.String(length=32), nullable=False),
                    sa.ForeignKeyConstraint(['created_by_uuid'], [u'user.uuid'], name=u'note_fk_created_by'),
                    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_table('note_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('parent_type', sa.String(length=20), autoincrement=False, nullable=True),
                    sa.Column('parent_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('type', sa.String(length=15), autoincrement=False, nullable=True),
                    sa.Column('subject', sa.String(length=255), autoincrement=False, nullable=True),
                    sa.Column('text', sa.Text(), autoincrement=False, nullable=True),
                    sa.Column('created', sa.DateTime(), autoincrement=False, nullable=True),
                    sa.Column('created_by_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
    )
    op.create_index(op.f('ix_note_version_end_transaction_id'), 'note_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_note_version_operation_type'), 'note_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_note_version_transaction_id'), 'note_version', ['transaction_id'], unique=False)


def downgrade():

    # note
    op.drop_index(op.f('ix_note_version_transaction_id'), table_name='note_version')
    op.drop_index(op.f('ix_note_version_operation_type'), table_name='note_version')
    op.drop_index(op.f('ix_note_version_end_transaction_id'), table_name='note_version')
    op.drop_table('note_version')
    op.drop_table('note')
