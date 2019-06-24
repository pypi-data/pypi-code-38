# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Helper methods for tests."""

import copy
import uuid

from flask import current_app
from invenio_db import db
from invenio_pidstore import current_pidstore
from invenio_records_rest.utils import deny_all
from six.moves import reduce

from invenio_circulation.api import Loan
from invenio_circulation.permissions import loan_reader
from invenio_circulation.pidstore.pids import CIRCULATION_LOAN_MINTER


class SwappedConfig:
    """Helper to hot-swap a configuration value."""

    def __init__(self, key, value):
        """Constructor."""
        self.key = key
        self.new_value = value

    def __enter__(self):
        """Save previous value and swap it with the new."""
        self.prev_value = current_app.config[self.key]
        current_app.config[self.key] = self.new_value

    def __exit__(self, type, value, traceback):
        """Restore previous value."""
        current_app.config[self.key] = self.prev_value


class SwappedNestedConfig:
    """Helper to hot-swap a nested configuration value."""

    def __init__(self, nested_keys, value):
        """Constructor."""
        self.nested_keys = nested_keys
        self.new_value = value

    def __enter__(self):
        """Save previous value and swap it with the new."""
        config_obj = reduce(dict.__getitem__, self.nested_keys[:-1],
                            current_app.config)
        self.prev_value = config_obj[self.nested_keys[-1]]
        config_obj[self.nested_keys[-1]] = self.new_value

    def __exit__(self, type, value, traceback):
        """Restore previous value."""
        config_obj = reduce(dict.__getitem__, self.nested_keys[:-1],
                            current_app.config)
        config_obj[self.nested_keys[-1]] = self.prev_value


def create_loan(data):
    """Create a test record."""
    with db.session.begin_nested():
        data = copy.deepcopy(data)
        rec_uuid = uuid.uuid4()
        pid = current_pidstore.minters[CIRCULATION_LOAN_MINTER](rec_uuid, data)
        record = Loan.create(data, id_=rec_uuid)
        return pid, record


def test_views_permissions_factory(action):
    """Test views permissions factory."""
    if action == 'loan-read-access':
        return loan_reader()
    else:
        return deny_all()
