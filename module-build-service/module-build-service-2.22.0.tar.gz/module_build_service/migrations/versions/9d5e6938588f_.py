"""Remove the COPR columns

Revision ID: 9d5e6938588f
Revises: 708ac8950f55
Create Date: 2018-06-28 13:57:08.977877

"""

revision = '9d5e6938588f'
down_revision = '708ac8950f55'

from alembic import op
import sqlalchemy as sa


def upgrade():
    with op.batch_alter_table('module_builds') as b:
        b.drop_column('copr_project')
        b.drop_column('copr_owner')


def downgrade():
    with op.batch_alter_table('module_builds') as b:
        b.add_column('copr_project', sa.VARCHAR(), nullable=True)
        b.add_column('copr_owner', sa.VARCHAR(), nullable=True)
