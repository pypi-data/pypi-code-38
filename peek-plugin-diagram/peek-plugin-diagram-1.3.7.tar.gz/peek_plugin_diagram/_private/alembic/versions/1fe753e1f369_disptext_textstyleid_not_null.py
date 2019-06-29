"""DispText.textStyleId not null

Peek Plugin Database Migration Script

Revision ID: 1fe753e1f369
Revises: bfdd4f46e293
Create Date: 2017-08-26 17:46:15.455355

"""

# revision identifiers, used by Alembic.
revision = '1fe753e1f369'
down_revision = 'bfdd4f46e293'
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.drop_index('idx_DispText_styleId', table_name='DispText',  schema='pl_diagram')

    op.alter_column('DispText', 'textStyleId', type_=sa.Integer, nullable=False,
                    schema='pl_diagram')
    op.create_index('idx_DispText_styleId', 'DispText', ['textStyleId'], unique=False, schema='pl_diagram')


def downgrade():
    op.alter_column('DispText', 'textStyleId', type_=sa.Integer, nullable=True,
                    schema='pl_diagram')
