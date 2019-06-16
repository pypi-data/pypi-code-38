# -*- coding: utf-8 -*-
"""add purchase_batch_row_claim

Revision ID: b5aa18867ab3
Revises: 977a76f259bd
Create Date: 2018-05-17 11:43:14.639019

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'b5aa18867ab3'
down_revision = u'977a76f259bd'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # purchase_batch_row_claim
    op.create_table('purchase_batch_row_claim',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('claiming_row_uuid', sa.String(length=32), nullable=False),
                    sa.Column('claimed_row_uuid', sa.String(length=32), nullable=False),
                    sa.Column('cases_received', sa.Numeric(precision=10, scale=4), nullable=True),
                    sa.Column('units_received', sa.Numeric(precision=10, scale=4), nullable=True),
                    sa.Column('cases_damaged', sa.Numeric(precision=10, scale=4), nullable=True),
                    sa.Column('units_damaged', sa.Numeric(precision=10, scale=4), nullable=True),
                    sa.Column('cases_expired', sa.Numeric(precision=10, scale=4), nullable=True),
                    sa.Column('units_expired', sa.Numeric(precision=10, scale=4), nullable=True),
                    sa.ForeignKeyConstraint(['claimed_row_uuid'], [u'purchase_batch_row.uuid'], name=u'purchase_batch_row_claim_fk_claimed_row'),
                    sa.ForeignKeyConstraint(['claiming_row_uuid'], [u'purchase_batch_row.uuid'], name=u'purchase_batch_row_claim_fk_claiming_row'),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():

    # purchase_batch_row_claim
    op.drop_table('purchase_batch_row_claim')
