"""Increased size of importGroupHash

Peek Plugin Database Migration Script

Revision ID: e9d80c4c087d
Revises: 4b943b584307
Create Date: 2017-10-25 10:03:26.694547

"""

# revision identifiers, used by Alembic.
revision = 'e9d80c4c087d'
down_revision = '4b943b584307'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():
    op.alter_column('DispBase', 'importGroupHash', type_=sa.String(length=200), nullable=True, schema='pl_diagram')


def downgrade():
    op.alter_column('DispBase', 'importGroupHash', type_=sa.String(length=100), nullable=True, schema='pl_diagram')
