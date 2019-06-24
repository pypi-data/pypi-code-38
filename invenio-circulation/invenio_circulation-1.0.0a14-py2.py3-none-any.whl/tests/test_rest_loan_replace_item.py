# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for loan update."""

import json

from flask import url_for

from invenio_circulation.api import get_loan_for_item


def _post(app, json_headers, loan, payload):
    with app.test_client() as client:
        url = url_for(
            "invenio_circulation_loan_replace_item.loan_replace_item_resource",
            pid_value=loan["loan_pid"],
        )
        res = client.post(url, headers=json_headers, data=json.dumps(payload))
        data = json.loads(res.data.decode("utf-8"))
    return res, data


def test_loan_replace_item(app, json_headers, params, indexed_loans):
    """Test that no Loan is returned for the given Item if only pendings."""
    item_pid = "item_on_loan_2"
    loan = get_loan_for_item(item_pid)
    payload = {"item_pid": "new_item_pid"}
    res, data = _post(app, json_headers, loan, payload)
    assert res.status == "202 ACCEPTED"
    assert data["metadata"]["item_pid"] == payload["item_pid"]
    # the ref won't change as it is pointing back to loan (it will
    # resolve by loan endpoint)
    assert data["metadata"]["item"]["ref"] == loan["loan_pid"]


def test_loan_replace_item_inactive_state(
    app, json_headers, params, indexed_loans
):
    """Test item replacement on a Loan that is not active."""
    for _pid, _loan in indexed_loans:
        if _loan["state"] == "ITEM_RETURNED":
            loan = _loan
            break
    payload = {"item_pid": "new_item_pid"}
    res, data = _post(app, json_headers, loan, payload)
    assert data["status"] == 400
    assert data["message"] == (
        "Cannot replace item in a loan that is not in active state. "
        "Current loan state '{}'".format(loan["state"])
    )


def test_loan_replace_item_wo_params(
    app, json_headers, params, indexed_loans
):
    """Test that no Loan is returned for the given Item if only pendings."""
    item_pid = "item_on_loan_2"
    loan = get_loan_for_item(item_pid)
    payload = {}
    res, data = _post(app, json_headers, loan, payload)
    assert res.status_code == 400


def test_loan_replace_item_wo_loan(app, json_headers, params, indexed_loans):
    """Test that no Loan is returned for the given Item if only pendings."""
    loan = {"loan_pid": "not_existing_one"}
    payload = {"item_pid": "item_on_loan_2"}
    res, data = _post(app, json_headers, loan, payload)
    assert data["status"] == 404
