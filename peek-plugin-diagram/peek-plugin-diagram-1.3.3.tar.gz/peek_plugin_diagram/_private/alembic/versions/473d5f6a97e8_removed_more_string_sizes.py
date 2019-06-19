"""removed more string sizes

Peek Plugin Database Migration Script

Revision ID: 473d5f6a97e8
Revises: 6f545d4166dc
Create Date: 2019-06-10 22:21:54.762566

"""

# revision identifiers, used by Alembic.
revision = '473d5f6a97e8'
down_revision = '6f545d4166dc'
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.alter_column('DispBase', 'importHash', type_=sa.String(), nullable=True,
                    schema='pl_diagram')
    op.alter_column('DispBase', 'importGroupHash', type_=sa.String(), nullable=True,
                    schema='pl_diagram')

    op.alter_column('LiveDbDispLink', 'dispAttrName', type_=sa.String(), nullable=False,
                    schema='pl_diagram')
    op.alter_column('LiveDbDispLink', 'liveDbKey', type_=sa.String(), nullable=False,
                    schema='pl_diagram')

    op.alter_column('LiveDbDispLink', 'importKeyHash', type_=sa.String(), nullable=True,
                    schema='pl_diagram')
    op.alter_column('LiveDbDispLink', 'importGroupHash', type_=sa.String(), nullable=True,
                    schema='pl_diagram')
    op.alter_column('LiveDbDispLink', 'importDispHash', type_=sa.String(), nullable=True,
                    schema='pl_diagram')
    op.alter_column('LiveDbDispLink', 'propsJson', type_=sa.String(), nullable=True,
                    schema='pl_diagram')

def downgrade():
    pass
