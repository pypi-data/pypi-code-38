# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for loan JSON schema."""
from copy import deepcopy
from json import loads

from pkg_resources import resource_string

from invenio_circulation.proxies import current_circulation

schema_in_bytes = resource_string(
    'invenio_circulation.schemas', 'loans/loan-v1.0.0.json'
)


def test_state_enum(app):
    """Test that schema Loan states corresponds to transitions states."""
    schema = loads(schema_in_bytes.decode('utf8'))
    state_dict = schema.get('properties').get('state')
    assert 'enum' in state_dict
    all_states = app.config['CIRCULATION_LOAN_TRANSITIONS'].keys()
    assert not (set(state_dict.get('enum')) - set(all_states))


def test_state_checkout_with_loan_pid(
    loan_created, db, params, mock_is_item_available_for_checkout
):
    """Test that created Loan validates after a checkout action."""
    new_params = deepcopy(params)
    new_params['trigger'] = 'checkout'
    loan = current_circulation.circulation.trigger(loan_created, **new_params)
    loan.validate()


def test_indexed_loans(indexed_loans):
    """Test mappings, index creation and loans indexing."""
    assert indexed_loans
