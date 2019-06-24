# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for loan states."""

import pytest
from invenio_indexer.api import RecordIndexer
from invenio_search import current_search

from invenio_circulation.api import get_loan_for_item
from invenio_circulation.errors import MultipleLoansOnItemError

from .helpers import create_loan


def test_api_circulation_item_loan_pending(app, indexed_loans):
    """Test that no Loan is returned for the given Item if only pendings."""
    pending_item_pid = "item_pending_1"
    loan = get_loan_for_item(pending_item_pid)
    assert loan is None


def test_api_circulation_item_no_loan(app, indexed_loans):
    """Test that no Loan is returned for the given Item if no loans."""
    not_loaned_item_pid = "item_not_loaned"
    loan = get_loan_for_item(not_loaned_item_pid)
    assert loan is None


def test_api_circulation_item_on_loan(app, indexed_loans):
    """Test that Loan is returned for the given Item if one active."""
    multiple_loans_pid = "item_multiple_pending_on_loan_7"
    loan = get_loan_for_item(multiple_loans_pid)
    assert loan['state'] == 'ITEM_ON_LOAN'
    assert loan['item_pid'] == multiple_loans_pid


def test_api_circulation_item_not_found(app, indexed_loans):
    """Test API GET call to check circulation item not found."""
    loan = get_loan_for_item("")
    assert loan is None


def test_multiple_active_loans(app, db, indexed_loans):
    """Test that raises if there are multiple active Loans for given Item."""
    multiple_loans_pid = "item_multiple_pending_on_loan_7"

    test_loan_data = {
        "item_pid": "item_multiple_pending_on_loan_7",
        "patron_pid": "2",
        "state": "ITEM_ON_LOAN",
        "transaction_date": "2018-06-26",
        "transaction_location_pid": "loc_pid",
        "transaction_user_pid": "user_pid",
        "start_date": "2018-07-24",
        "end_date": "2018-08-23"
    }

    pid, loan = create_loan(test_loan_data)
    db.session.commit()
    RecordIndexer().index(loan)
    current_search.flush_and_refresh(index="loans")

    with pytest.raises(MultipleLoansOnItemError):
        get_loan_for_item(multiple_loans_pid)
