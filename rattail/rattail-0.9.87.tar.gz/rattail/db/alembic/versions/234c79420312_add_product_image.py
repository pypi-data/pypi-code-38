# -*- coding: utf-8 -*-
"""add product_image

Revision ID: 234c79420312
Revises: 7ba105af22a7
Create Date: 2017-02-22 22:43:58.290180

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '234c79420312'
down_revision = u'7ba105af22a7'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # product_image
    op.create_table('product_image',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('product_uuid', sa.String(length=32), nullable=False),
                    sa.Column('bytes', sa.LargeBinary(), nullable=False),
                    sa.ForeignKeyConstraint(['product_uuid'], [u'product.uuid'], name=u'product_image_fk_product'),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():

    # product_image
    op.drop_table('product_image')
