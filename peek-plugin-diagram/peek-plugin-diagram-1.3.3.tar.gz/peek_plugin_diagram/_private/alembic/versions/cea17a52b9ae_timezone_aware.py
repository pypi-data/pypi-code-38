"""timezone aware

Peek Plugin Database Migration Script

Revision ID: cea17a52b9ae
Revises: 34dd05f474df
Create Date: 2017-12-31 14:29:21.485753

"""

# revision identifiers, used by Alembic.
revision = 'cea17a52b9ae'
down_revision = '34dd05f474df'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():

    # pl_diagram."DispBase"
    op.execute('''ALTER TABLE pl_diagram."DispBase"
                  ALTER COLUMN "importUpdateDate" TYPE TIMESTAMP WITH TIME ZONE
                  USING "importUpdateDate" AT TIME ZONE 'UTC'
               ''')


def downgrade():
    pass