# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test API permissions."""

import json

from flask import url_for
from invenio_accounts.models import User
from invenio_accounts.testutils import login_user_via_session


def _get(app, json_headers, pid_value, user_email=None):
    """Perform API GET with the given param."""
    with app.test_client() as client:
        if user_email:
            login_user_via_session(client, email=user_email)

        url = url_for('invenio_circulation_loan_for_item.loan_resource',
                      pid_value=pid_value)
        res = client.get(url, headers=json_headers)

    payload = None
    if res.status_code == 200:
        payload = json.loads(res.data.decode('utf-8'))
    return res, payload


def test_default_permission_factory(app, json_headers, indexed_loans):
    """Test default permission factory."""
    multiple_loans_pid = "item_multiple_pending_on_loan_7"
    res, _ = _get(app, json_headers, multiple_loans_pid)
    assert res.status_code == 200


def test_loan_access_anonymous(app, json_headers, indexed_loans, users):
    """Test access for anonymous user to items loan endpoint."""
    multiple_loans_pid = "item_multiple_pending_on_loan_7"
    res, _ = _get(app, json_headers, multiple_loans_pid)
    assert res.status_code == 401


def test_logged_user_no_access(app, json_headers, indexed_loans, users):
    """Test access for user with no right to see the loan."""
    user = users['user']
    user_email = User.query.get(user.id).email

    multiple_loans_pid = "item_multiple_pending_on_loan_7"
    res, payload = _get(app, json_headers, multiple_loans_pid, user_email)
    assert res.status_code == 403


def test_logged_user_access_granted(app, json_headers, indexed_loans, users):
    """Test access for user with a right to see the loan."""
    user = users['manager']
    user_email = User.query.get(user.id).email

    multiple_loans_pid = "item_multiple_pending_on_loan_7"
    res, payload = _get(app, json_headers, multiple_loans_pid, user_email)
    assert res.status_code == 200
    assert payload['metadata']['item_pid'] == multiple_loans_pid
