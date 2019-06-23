"""Added textHeight to DispText

Peek Plugin Database Migration Script

Revision ID: d6e25d8ba156
Revises: 2127d894e46b
Create Date: 2017-08-14 13:27:08.675775

"""

# revision identifiers, used by Alembic.
revision = 'd6e25d8ba156'
down_revision = '2127d894e46b'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():

    op.add_column('DispText',
                  sa.Column('textHeight', sa.Float(), nullable=True),
                  schema='pl_diagram')

    op.add_column('DispText',
                  sa.Column('textHStretch', sa.Float(), nullable=True, server_default='1.0'),
                  schema='pl_diagram')


    op.execute('''
    UPDATE "pl_diagram"."DispText"
    SET "textHStretch" = 1.0
    ''')

    op.alter_column('DispText', 'textHStretch',
                    existing_type=sa.Float(),
                    nullable=False,
                    schema='pl_diagram')


def downgrade():
    raise NotImplementedError("Downgrade is not implemented")