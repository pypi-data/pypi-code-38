"""timezone aware

Peek Plugin Database Migration Script

Revision ID: 2119b6aab2c5
Revises: 0f8cf37f3af3
Create Date: 2017-12-31 14:29:39.875909

"""

# revision identifiers, used by Alembic.
revision = '2119b6aab2c5'
down_revision = '0f8cf37f3af3'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():
    # pl_inbox."Task"
    op.execute('''ALTER TABLE pl_inbox."Task"
                  ALTER COLUMN "dateTime" TYPE TIMESTAMP WITH TIME ZONE
                  USING "dateTime" AT TIME ZONE 'UTC'
               ''')

    op.execute('''ALTER TABLE pl_inbox."Task"
                  ALTER COLUMN "autoDeleteDateTime" TYPE TIMESTAMP WITH TIME ZONE
                  USING "autoDeleteDateTime" AT TIME ZONE 'UTC'
               ''')

    # pl_inbox."Activity"
    op.execute('''ALTER TABLE pl_inbox."Activity"
                  ALTER COLUMN "dateTime" TYPE TIMESTAMP WITH TIME ZONE
                  USING "dateTime" AT TIME ZONE 'UTC'
               ''')

    op.execute('''ALTER TABLE pl_inbox."Activity"
                  ALTER COLUMN "autoDeleteDateTime" TYPE TIMESTAMP WITH TIME ZONE
                  USING "autoDeleteDateTime" AT TIME ZONE 'UTC'
               ''')


def downgrade():
    pass
