# -*- coding: utf-8 -*-
"""fix user_x_role null bug

Revision ID: 3a7029aed67
Revises: 35b1da3be8f5
Create Date: 2015-08-11 11:36:41.908780

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '3a7029aed67'
down_revision = u'35b1da3be8f5'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # user_x_role

    # first remove all records with nulls
    user_x_role = sa.sql.table('user_x_role',
                               sa.sql.column('role_uuid'),
                               sa.sql.column('user_uuid'))
    op.execute(user_x_role.delete().where(user_x_role.c.role_uuid == None))
    op.execute(user_x_role.delete().where(user_x_role.c.user_uuid == None))

    # okay, now can disallow nulls
    op.alter_column('user_x_role', 'role_uuid',
               existing_type=sa.String(length=32),
               nullable=False)
    op.alter_column('user_x_role', 'user_uuid',
               existing_type=sa.String(length=32),
               nullable=False)


def downgrade():

    # user_x_role
    op.alter_column('user_x_role', 'user_uuid',
               existing_type=sa.String(length=32),
               nullable=True)
    op.alter_column('user_x_role', 'role_uuid',
               existing_type=sa.String(length=32),
               nullable=True)
