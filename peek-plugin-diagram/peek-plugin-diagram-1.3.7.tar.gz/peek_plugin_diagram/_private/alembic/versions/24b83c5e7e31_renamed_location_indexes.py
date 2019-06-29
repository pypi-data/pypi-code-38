"""Renamed Location indexes

Peek Plugin Database Migration Script

Revision ID: 24b83c5e7e31
Revises: 23117803d414
Create Date: 2017-09-09 23:45:23.530049

"""

# revision identifiers, used by Alembic.
revision = '24b83c5e7e31'
down_revision = '23117803d414'
branch_labels = None
depends_on = None

from alembic import op


def upgrade():
    op.drop_index('idx_DKIndexUpdate_gridKey', table_name='LocationIndexCompiled',
                  schema='pl_diagram')
    op.drop_index('idx_DKIndexUpdate_coordSetId', table_name='LocationIndexCompiled',
                  schema='pl_diagram')
    op.drop_index('idx_DKCompQueue_coordSetId_gridKey',
                  table_name='LocationIndexCompilerQueue', schema='pl_diagram')

    op.create_index('idx_LIIndexUpdate_indexBucket', 'LocationIndexCompiled',
                    ['indexBucket'], unique=True, schema='pl_diagram')
    op.create_index('idx_LIIndexUpdate_modelSetId', 'LocationIndexCompiled',
                    ['modelSetId'], unique=False, schema='pl_diagram')
    op.create_index('idx_LICompQueue_modelSetId_indexBucket',
                    'LocationIndexCompilerQueue', ['modelSetId', 'indexBucket'],
                    unique=False, schema='pl_diagram')
    # ### end Alembic commands ###


def downgrade():
    raise NotImplementedError("Downgrade not implemented")
