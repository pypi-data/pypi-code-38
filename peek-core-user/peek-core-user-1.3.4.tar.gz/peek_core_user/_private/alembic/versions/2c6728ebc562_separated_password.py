"""separated password

Peek Plugin Database Migration Script

Revision ID: 2c6728ebc562
Revises: 9b65be31926e
Create Date: 2018-01-28 16:39:17.645627

"""

# revision identifiers, used by Alembic.
revision = '2c6728ebc562'
down_revision = '9b65be31926e'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():

    op.create_table('InternalUserPassword',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('userId', sa.Integer(), nullable=False),
    sa.Column('password', sa.String(length=50), nullable=False),
    sa.ForeignKeyConstraint(['userId'], ['core_user.InternalUser.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    schema='core_user'
    )

    op.execute('''
    INSERT INTO core_user."InternalUserPassword" ("userId", "password")
    SELECT "id", "password"
    FROM core_user."InternalUser"
    WHERE "password" is not null
    ''')

    op.drop_column('InternalUser', 'password', schema='core_user')



def downgrade():
    raise NotImplementedError("Downgrade not implemented")
