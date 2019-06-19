"""fix task priorities

Peek Plugin Database Migration Script

Revision ID: 36a9bc546606
Revises: 543ec701c9f7
Create Date: 2017-04-18 09:52:20.935251

"""

# revision identifiers, used by Alembic.
revision = '36a9bc546606'
down_revision = '543ec701c9f7'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():
    op.execute('''UPDATE "pl_inbox"."Task"
                  SET "displayPriority" = 1
                  WHERE "displayPriority" = 0;''')


def downgrade():
    pass
