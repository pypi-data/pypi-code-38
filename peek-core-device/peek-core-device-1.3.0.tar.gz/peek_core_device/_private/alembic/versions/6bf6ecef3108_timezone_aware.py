"""timezone aware

Peek Plugin Database Migration Script

Revision ID: 6bf6ecef3108
Revises: 5dd43ff7ea8e
Create Date: 2017-12-31 14:28:47.653836

"""

# revision identifiers, used by Alembic.
revision = '6bf6ecef3108'
down_revision = '5dd43ff7ea8e'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():

    # core_device."DeviceInfo"
    op.execute('''ALTER TABLE core_device."DeviceInfo"
                  ALTER COLUMN "lastOnline" TYPE TIMESTAMP WITH TIME ZONE
                  USING "lastOnline" AT TIME ZONE 'UTC'
               ''')

    op.execute('''ALTER TABLE core_device."DeviceInfo"
                  ALTER COLUMN "lastUpdateCheck" TYPE TIMESTAMP WITH TIME ZONE
                  USING "lastUpdateCheck" AT TIME ZONE 'UTC'
               ''')

    op.execute('''ALTER TABLE core_device."DeviceInfo"
                  ALTER COLUMN "createdDate" TYPE TIMESTAMP WITH TIME ZONE
                  USING "createdDate" AT TIME ZONE 'UTC'
               ''')


    # core_device."DeviceUpdate"
    op.execute('''ALTER TABLE core_device."DeviceUpdate"
                  ALTER COLUMN "buildDate" TYPE TIMESTAMP WITH TIME ZONE
                  USING "buildDate" AT TIME ZONE 'UTC'
               ''')

def downgrade():
    pass