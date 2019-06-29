"""timezone aware

Peek Plugin Database Migration Script

Revision ID: 9b65be31926e
Revises: 56d805072d2a
Create Date: 2017-12-31 14:32:42.351711

"""

# revision identifiers, used by Alembic.
revision = '9b65be31926e'
down_revision = '56d805072d2a'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():
    # core_user."UserLoggedIn"
    op.execute('''ALTER TABLE core_user."UserLoggedIn"
                  ALTER COLUMN "loggedInDateTime" TYPE TIMESTAMP WITH TIME ZONE
                  USING "loggedInDateTime" AT TIME ZONE 'UTC'
               ''')


def downgrade():
    pass
