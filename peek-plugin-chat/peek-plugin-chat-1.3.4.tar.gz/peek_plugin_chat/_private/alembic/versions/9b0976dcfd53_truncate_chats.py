"""Truncate chats

Peek Plugin Database Migration Script

Revision ID: 9b0976dcfd53
Revises: 5288d02e94e4
Create Date: 2017-12-27 10:03:38.828892

"""

# revision identifiers, used by Alembic.
revision = '9b0976dcfd53'
down_revision = '5288d02e94e4'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():
    op.execute(' TRUNCATE TABLE pl_chat."ChatTuple" CASCADE ')


def downgrade():
    pass