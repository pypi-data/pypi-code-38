"""Increased size of disp.json

Peek Plugin Database Migration Script

Revision ID: cbd5e370686f
Revises: 9e7ca1acd6be
Create Date: 2017-08-12 17:34:00.532517

"""

# revision identifiers, used by Alembic.
revision = 'cbd5e370686f'
down_revision = '9e7ca1acd6be'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():

    op.alter_column('DispBase', 'dispJson',
               existing_type=sa.VARCHAR(length=200000),
               nullable=True,
               schema='pl_diagram')

    op.alter_column('DispPolygon', 'geomJson',
               existing_type=sa.VARCHAR(length=200000),
               nullable=False,
               schema='pl_diagram')

    op.alter_column('DispPolyline', 'geomJson',
               existing_type=sa.VARCHAR(length=200000),
               nullable=False,
               schema='pl_diagram')


def downgrade():
    raise Exception("Downgrade is not implemented")