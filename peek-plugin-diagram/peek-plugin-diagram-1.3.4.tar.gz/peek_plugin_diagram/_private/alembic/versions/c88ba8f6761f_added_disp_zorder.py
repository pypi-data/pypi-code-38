"""added disp zOrder

Peek Plugin Database Migration Script

Revision ID: c88ba8f6761f
Revises: 4925c894757b
Create Date: 2017-11-26 12:52:22.016867

"""

# revision identifiers, used by Alembic.
revision = 'c88ba8f6761f'
down_revision = '4925c894757b'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('DispBase', sa.Column('zOrder', sa.Integer(), server_default='0', nullable=True), schema='pl_diagram')
    op.execute(''' UPDATE "pl_diagram"."DispBase" SET "zOrder" = 0 ''')
    op.alter_column('DispBase', 'zOrder', type_=sa.Integer, nullable=False, schema='pl_diagram')


def downgrade():
    op.drop_column('DispBase', 'zOrder', schema='pl_diagram')
