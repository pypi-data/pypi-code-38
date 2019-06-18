"""Add reused_component_id

Revision ID: a1fc0736bca8
Revises: 0ef60c3ed440
Create Date: 2017-02-10 19:32:35.288596

"""

# revision identifiers, used by Alembic.
revision = 'a1fc0736bca8'
down_revision = '0ef60c3ed440'

from alembic import op
import sqlalchemy as sa


def upgrade():
    with op.batch_alter_table('component_builds') as b:
        b.add_column(sa.Column('reused_component_id', sa.Integer(), nullable=True))
        b.create_foreign_key('component_builds', 'component_builds', ['reused_component_id'], ['id'])
        b.add_column(sa.Column('ref', sa.String(), nullable=True))


def downgrade():
    with op.batch_alter_table('component_builds') as b:
        b.drop_constraint('component_builds', type_='foreignkey')
        b.drop_column('reused_component_id')
        b.drop_column('ref')
