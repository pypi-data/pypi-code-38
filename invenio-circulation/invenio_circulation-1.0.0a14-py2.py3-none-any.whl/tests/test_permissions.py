# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test circulation permissions on transitions."""

import pytest
from invenio_records_rest.utils import allow_all, deny_all

from invenio_circulation.errors import InvalidPermissionError
from invenio_circulation.transitions.transitions import CreatedToPending


def test_valid_permission(loan_created, params):
    """Test transition with valid permission."""
    transition = CreatedToPending(
        'CREATED', 'PENDING', trigger='next', permission_factory=allow_all
    )
    transition.execute(loan_created, **params)
    assert loan_created['state'] == 'PENDING'


def test_invalid_permission(loan_created, params):
    """Test transition without permission."""
    transition = CreatedToPending(
        'CREATED', 'PENDING', trigger='next', permission_factory=deny_all
    )
    with pytest.raises(InvalidPermissionError):
        transition.execute(loan_created, **params)
    assert loan_created['state'] == 'CREATED'
