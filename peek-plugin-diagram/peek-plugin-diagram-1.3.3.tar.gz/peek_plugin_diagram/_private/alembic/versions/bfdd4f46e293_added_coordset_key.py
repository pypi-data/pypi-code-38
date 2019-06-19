"""added CoordSet key

Peek Plugin Database Migration Script

Revision ID: bfdd4f46e293
Revises: 2c5f47322bda
Create Date: 2017-08-24 14:08:48.525689

"""

# revision identifiers, used by Alembic.
revision = 'bfdd4f46e293'
down_revision = '2c5f47322bda'
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.add_column('ModelCoordSet', sa.Column('key', sa.String(length=50), nullable=True),
                  schema='pl_diagram')
    op.execute(''' UPDATE "pl_diagram"."ModelCoordSet" SET "key" = "name" ''')
    op.alter_column('ModelCoordSet', 'key', type_=sa.String(length=50), nullable=False,
                    schema='pl_diagram')


def downgrade():
    raise NotImplemented
