"""rebuild location index

Peek Plugin Database Migration Script

Revision ID: 34dd05f474df
Revises: 298b291aac2d
Create Date: 2017-12-29 20:00:27.258810

"""

# revision identifiers, used by Alembic.
revision = '34dd05f474df'
down_revision = '298b291aac2d'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():
    op.execute('''
        TRUNCATE TABLE pl_diagram."LocationIndexCompiled" CASCADE
    ''')

    op.execute('''
        INSERT INTO pl_diagram."LocationIndexCompilerQueue"
        ("modelSetId", "indexBucket")
        SELECT "modelSetId", "indexBucket"
        FROM pl_diagram."LocationIndex"
    ''')


def downgrade():
    pass