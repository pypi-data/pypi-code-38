# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Create pidrelations tables."""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '1d4e361b7586'
down_revision = '2216c32d7059'  # Create branch
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    op.create_table(
        'pidrelations_pidrelation',
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('updated', sa.DateTime(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=False),
        sa.Column('child_id', sa.Integer(), nullable=False),
        sa.Column('relation_type', sa.SmallInteger(), nullable=False),
        sa.Column('index', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['child_id'], ['pidstore_pid.id'],
            name=op.f('fk_pidrelations_pidrelation_child_id_pidstore_pid'),
            onupdate='CASCADE', ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['parent_id'], ['pidstore_pid.id'],
            name=op.f('fk_pidrelations_pidrelation_parent_id_pidstore_pid'),
            onupdate='CASCADE', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint(
            'parent_id', 'child_id', name=op.f('pk_pidrelations_pidrelation')
        )
    )


def downgrade():
    """Downgrade database."""
    op.drop_table('pidrelations_pidrelation')
