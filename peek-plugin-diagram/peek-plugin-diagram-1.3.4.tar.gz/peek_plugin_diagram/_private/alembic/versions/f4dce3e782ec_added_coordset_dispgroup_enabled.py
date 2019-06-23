"""Added CoordSet dispGroup enabled

Peek Plugin Database Migration Script

Revision ID: f4dce3e782ec
Revises: 81c1d2809046
Create Date: 2019-05-17 14:37:07.220197

"""

# revision identifiers, used by Alembic.
revision = 'f4dce3e782ec'
down_revision = '81c1d2809046'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():
    op.add_column('ModelCoordSet',
                  sa.Column('dispGroupTemplatesEnabled', sa.Boolean(),
                            server_default='false', nullable=True),
                  schema='pl_diagram')

    op.execute('UPDATE "pl_diagram"."ModelCoordSet" SET "dispGroupTemplatesEnabled" = false ')

    op.alter_column('ModelCoordSet', 'dispGroupTemplatesEnabled', type_=sa.Boolean(),
                    nullable=False, schema='pl_diagram')


def downgrade():
    op.drop_column('ModelCoordSet', 'dispGroupTemplatesEnabled', schema='pl_diagram')