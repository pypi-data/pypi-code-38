"""Removed string lengths

Peek Plugin Database Migration Script

Revision ID: 19b2a8d326ad
Revises: ab9da4532175
Create Date: 2019-06-10 21:52:38.648849

"""

# revision identifiers, used by Alembic.
revision = '19b2a8d326ad'
down_revision = 'ab9da4532175'
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.alter_column('LiveDbItem', 'key', type_=sa.String(), nullable=False,
                    schema='pl_livedb')
    op.alter_column('LiveDbItem', 'rawValue', type_=sa.String(), nullable=True,
                    schema='pl_livedb')
    op.alter_column('LiveDbItem', 'displayValue', type_=sa.String(), nullable=True,
                    schema='pl_livedb')
    op.alter_column('LiveDbItem', 'importHash', type_=sa.String(), nullable=True,
                    schema='pl_livedb')
    op.alter_column('LiveDbItem', 'propsJson', type_=sa.String(), nullable=True,
                    schema='pl_livedb')

    op.alter_column('LiveDbModelSet', 'name', type_=sa.String(), nullable=False,
                    schema='pl_livedb')
    op.alter_column('LiveDbModelSet', 'propsJson', type_=sa.String(), nullable=True,
                    schema='pl_livedb')


def downgrade():
    pass
