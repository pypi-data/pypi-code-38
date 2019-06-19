""" Updates for DispGroup

Peek Plugin Database Migration Script

Revision ID: 8ef78f862ac8
Revises: 1b17ef0cca17
Create Date: 2019-02-17 13:45:55.038615

"""

# revision identifiers, used by Alembic.
revision = '8ef78f862ac8'
down_revision = '1b17ef0cca17'
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.add_column('DispGroup',
                  sa.Column('compileAsTemplate', sa.Boolean(), server_default='false',
                            nullable=False), schema='pl_diagram')

    op.drop_constraint('DispGroupPointer_groupId_fkey', 'DispGroupPointer',
                       schema='pl_diagram', type_='foreignkey')
    op.drop_index('idxDispGroupPointer_groupId', table_name='DispGroupPointer',
                  schema='pl_diagram')
    op.alter_column('DispGroupPointer', 'groupId', new_column_name='targetDispGroupId',
                    type_=sa.INTEGER(), nullable=True,
                    schema='pl_diagram')
    op.create_index('idxDispGroupPointer_targetDispGroupId', 'DispGroupPointer',
                    ['targetDispGroupId'], unique=False, schema='pl_diagram')
    op.create_foreign_key(None, 'DispGroupPointer', 'DispGroup', ['targetDispGroupId'],
                          ['id'], source_schema='pl_diagram',
                          referent_schema='pl_diagram', ondelete='SET NULL')

    op.add_column('DispBase', sa.Column('groupId', sa.Integer(), nullable=True),
                  schema='pl_diagram')
    op.create_index('idx_Disp_groupId', 'DispBase', ['groupId'], unique=False, schema='pl_diagram')
    op.create_foreign_key(None, 'DispBase', 'DispBase', ['groupId'], ['id'],
                          source_schema='pl_diagram', referent_schema='pl_diagram',
                          ondelete='CASCADE')

    op.drop_table('DispGroupItem', schema='pl_diagram')


def downgrade():
    raise NotImplementedError()
