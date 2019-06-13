# -*- coding: utf-8; -*-
"""add report_output.params

Revision ID: abd43933c6c6
Revises: 90d5e8185d44
Create Date: 2019-05-07 16:50:24.936129

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = 'abd43933c6c6'
down_revision = u'90d5e8185d44'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # report_output
    op.add_column('report_output', sa.Column('report_type', sa.String(length=255), nullable=True))
    op.add_column('report_output', sa.Column('params', rattail.db.types.JSONTextDict(), nullable=True))


def downgrade():

    # report_output
    op.drop_column('report_output', 'params')
    op.drop_column('report_output', 'report_type')
