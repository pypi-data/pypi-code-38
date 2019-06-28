# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Create pidrelations branch."""

import sqlalchemy as sa
from alembic import op

revision = '2216c32d7059'
down_revision = None
branch_labels = (u'invenio_pidrelations',)
depends_on = '999c62899c20'  # invenio-pidstore create tables


def upgrade():
    """Upgrade database."""


def downgrade():
    """Downgrade database."""
