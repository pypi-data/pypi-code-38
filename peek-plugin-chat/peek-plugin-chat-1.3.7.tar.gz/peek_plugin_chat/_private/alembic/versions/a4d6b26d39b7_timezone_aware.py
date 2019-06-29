"""timezone aware

Peek Plugin Database Migration Script

Revision ID: a4d6b26d39b7
Revises: 9b0976dcfd53
Create Date: 2017-12-31 14:29:07.288567

"""

# revision identifiers, used by Alembic.
revision = 'a4d6b26d39b7'
down_revision = '9b0976dcfd53'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():

    # pl_chat."DeviceInfo"
    op.execute('''ALTER TABLE pl_chat."ChatTuple"
                  ALTER COLUMN "lastActivity" TYPE TIMESTAMP WITH TIME ZONE
                  USING "lastActivity" AT TIME ZONE 'UTC'
               ''')

    # pl_chat."ChatUserTuple"
    op.execute('''ALTER TABLE pl_chat."ChatUserTuple"
                  ALTER COLUMN "lastReadDate" TYPE TIMESTAMP WITH TIME ZONE
                  USING "lastReadDate" AT TIME ZONE 'UTC'
               ''')

    # pl_chat."MessageTuple"
    op.execute('''ALTER TABLE pl_chat."MessageTuple"
                  ALTER COLUMN "dateTime" TYPE TIMESTAMP WITH TIME ZONE
                  USING "dateTime" AT TIME ZONE 'UTC'
               ''')


def downgrade():
    pass