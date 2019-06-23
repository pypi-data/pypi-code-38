"""Encoded Grids are now GridTuples

Peek Plugin Database Migration Script

Revision ID: 298b291aac2d
Revises: c88ba8f6761f
Create Date: 2017-12-16 19:30:54.032544

"""

# revision identifiers, used by Alembic.
revision = '298b291aac2d'
down_revision = 'c88ba8f6761f'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():
    op.execute(' TRUNCATE TABLE pl_diagram."GridKeyIndexCompiled" ')
    op.alter_column('GridKeyIndexCompiled', 'blobData', type_=sa.LargeBinary, new_column_name="encodedGridTuple",
                    schema='pl_diagram')
    op.execute('''INSERT INTO pl_diagram."GridKeyCompilerQueue" ("gridKey", "coordSetId")
                SELECT DISTINCT "gridKey", "coordSetId"
                FROM pl_diagram."GridKeyIndex"
                ''')


def downgrade():
    raise Exception("Downgrade is not implemented")

