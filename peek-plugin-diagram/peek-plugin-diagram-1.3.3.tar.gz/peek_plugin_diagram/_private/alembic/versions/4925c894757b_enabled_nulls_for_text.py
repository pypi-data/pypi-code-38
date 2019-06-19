"""enabled nulls for text

Peek Plugin Database Migration Script

Revision ID: 4925c894757b
Revises: e9d80c4c087d
Create Date: 2017-11-04 14:43:04.703237

"""

# revision identifiers, used by Alembic.
revision = '4925c894757b'
down_revision = 'e9d80c4c087d'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():
    op.alter_column('DispText', 'text', type_=sa.String(), nullable=True, schema='pl_diagram')


def downgrade():
    op.alter_column('DispText', 'text', type_=sa.String(length=1000), nullable=False, schema='pl_diagram')
