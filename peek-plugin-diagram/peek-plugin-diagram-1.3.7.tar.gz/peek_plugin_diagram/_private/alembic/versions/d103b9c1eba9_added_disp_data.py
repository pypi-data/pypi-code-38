"""Added disp data

Peek Plugin Database Migration Script

Revision ID: d103b9c1eba9
Revises: 558bc7fc4d36
Create Date: 2017-09-23 14:58:37.938811

"""

# revision identifiers, used by Alembic.
revision = 'd103b9c1eba9'
down_revision = '558bc7fc4d36'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():
    op.add_column('DispBase', sa.Column('dataJson', sa.String(length=500), nullable=True), schema='pl_diagram')


def downgrade():
    op.drop_column('DispBase', 'dataJson', schema='pl_diagram')