# -*- coding: utf-8 -*-
"""add purchase.department

Revision ID: 4bd528bca236
Revises: 9740f0dcf84b
Create Date: 2016-12-09 12:21:32.663614

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '4bd528bca236'
down_revision = u'9740f0dcf84b'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


batch_id_seq = sa.Sequence('batch_id_seq')


def upgrade():

    # purchase
    op.add_column('purchase', sa.Column('department_uuid', sa.String(length=32), nullable=True))
    op.create_foreign_key(u'purchase_fk_department', 'purchase', 'department', ['department_uuid'], ['uuid'])

    # purchase_batch
    op.add_column('purchase_batch', sa.Column('department_uuid', sa.String(length=32), nullable=True))
    op.create_foreign_key(u'purchase_batch_fk_department', 'purchase_batch', 'department', ['department_uuid'], ['uuid'])


def downgrade():

    # purchase_batch
    op.drop_constraint(u'purchase_batch_fk_department', 'purchase_batch', type_='foreignkey')
    op.drop_column('purchase_batch', 'department_uuid')

    # purchase_batch
    op.drop_constraint(u'purchase_fk_department', 'purchase', type_='foreignkey')
    op.drop_column('purchase', 'department_uuid')
