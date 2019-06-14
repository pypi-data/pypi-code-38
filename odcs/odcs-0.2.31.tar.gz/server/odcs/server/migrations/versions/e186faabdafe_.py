"""Add modular_koji_tags and module_defaults_url columns.

Revision ID: e186faabdafe
Revises: b2725d046624
Create Date: 2019-01-28 08:15:35.059106

"""

# revision identifiers, used by Alembic.
revision = 'e186faabdafe'
down_revision = 'b2725d046624'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('composes', sa.Column('modular_koji_tags', sa.String(), nullable=True))
    op.add_column('composes', sa.Column('module_defaults_url', sa.String(), nullable=True))


def downgrade():
    op.drop_column('composes', 'module_defaults_url')
    op.drop_column('composes', 'modular_koji_tags')
