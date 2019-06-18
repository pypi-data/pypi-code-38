"""Add a missing uniqueness constraint to module_builds_to_module_buildrequires

Revision ID: 65ad4fcdbce6
Revises: 6d503efcd2b8
Create Date: 2019-04-30 19:56:38.447195

"""

# revision identifiers, used by Alembic.
revision = '65ad4fcdbce6'
down_revision = '6d503efcd2b8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    with op.batch_alter_table('module_builds_to_module_buildrequires') as b:
        b.create_unique_constraint('unique_buildrequires', ['module_id', 'module_buildrequire_id'])


def downgrade():
    with op.batch_alter_table('module_builds_to_module_buildrequires') as b:
        b.drop_constraint('unique_buildrequires', type_='unique')
