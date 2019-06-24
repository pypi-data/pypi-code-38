# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for loan states."""

import json

from flask import url_for
from invenio_indexer.api import RecordIndexer
from invenio_search import current_search

from .helpers import create_loan


def _get(app, json_headers, pid_value):
    """Perform API GET with the given param."""
    with app.test_client() as client:
        url = url_for('invenio_circulation_loan_for_item.loan_resource',
                      pid_value=pid_value)
        res = client.get(url, headers=json_headers)

    payload = None
    if res.status_code == 200:
        payload = json.loads(res.data.decode('utf-8'))
    return res, payload


def test_rest_circulation_item_loan_pending(app, json_headers, indexed_loans):
    """Test API GET call to check item's pending loan."""
    pending_item_pid = "item_pending_1"
    res, payload = _get(app, json_headers, pending_item_pid)
    assert res.status_code == 200
    assert payload == {}


def test_rest_circulation_item_no_loan(app, json_headers, indexed_loans):
    """Test API GET call to check circulation when no loan on the item."""
    not_loaned_item_pid = "item_not_loaned"
    res, payload = _get(app, json_headers, not_loaned_item_pid)
    assert res.status_code == 200
    assert payload == {}


def test_rest_circulation_item_on_loan(app, json_headers, indexed_loans):
    """Test API GET call to check circulation item's loan."""
    multiple_loans_pid = "item_multiple_pending_on_loan_7"
    res, payload = _get(app, json_headers, multiple_loans_pid)
    assert res.status_code == 200
    loan = payload['metadata']
    assert loan['state'] == 'ITEM_ON_LOAN'
    assert loan['item_pid'] == multiple_loans_pid


def test_rest_circulation_item_not_found(app, json_headers, indexed_loans):
    """Test API GET call to check circulation item not found."""
    res, payload = _get(app, json_headers, "")
    assert res.status_code == 404


def test_multiple_active_loans(app, db, json_headers, indexed_loans):
    """Test return error when more than one loan on given item."""
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

    res, data = _get(app, json_headers, multiple_loans_pid)
    assert res.status_code == 400
