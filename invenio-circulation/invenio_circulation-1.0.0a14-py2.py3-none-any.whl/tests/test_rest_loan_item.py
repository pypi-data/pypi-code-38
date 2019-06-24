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
from invenio_db import db

from invenio_circulation.pidstore.fetchers import loan_pid_fetcher
from invenio_circulation.proxies import current_circulation
from invenio_circulation.views import build_url_action_for_pid


def test_rest_get_loan(app, json_headers, loan_created):
    """Test API GET call to fetch a loan by PID."""
    loan_pid = loan_pid_fetcher(loan_created.id, loan_created)
    expected_links = {
        'actions': {
            'request': build_url_action_for_pid(loan_pid, 'request'),
            'checkout': build_url_action_for_pid(loan_pid, 'checkout')
        }
    }

    with app.test_client() as client:
        url = url_for('invenio_records_rest.loanid_item',
                      pid_value=loan_pid.pid_value)
        res = client.get(url, headers=json_headers)

    assert res.status_code == 200
    loan_dict = json.loads(res.data.decode('utf-8'))
    assert loan_dict['metadata']['state'] == loan_created['state']
    assert loan_dict['links'] == expected_links


def _post(app, json_headers, params, pid_value, action):
    """Perform API POST with the given param."""
    with app.test_client() as client:
        url = url_for('invenio_circulation_loan_actions.loanid_actions',
                      pid_value=pid_value, action=action)
        res = client.post(url, headers=json_headers, data=json.dumps(params))
        payload = json.loads(res.data.decode('utf-8'))
    return res, payload


def test_rest_explicit_loan_valid_action(
    app, json_headers, params, mock_is_item_available_for_checkout,
    loan_created
):
    """Test API valid action on loan."""
    loan_pid = loan_pid_fetcher(loan_created.id, loan_created)

    res, payload = _post(app, json_headers, params,
                         pid_value=loan_pid.pid_value, action='checkout')
    assert res.status_code == 202
    assert payload['metadata']['state'] == 'ITEM_ON_LOAN'


def test_rest_automatic_loan_valid_action(
    app, json_headers, params, loan_created
):
    """Test API valid action on loan."""
    loan = current_circulation.circulation.trigger(
        loan_created,
        **dict(params, trigger='request',
               pickup_location_pid='pickup_location_pid')
    )
    db.session.commit()
    assert loan['state'] == 'PENDING'

    app.config[
        'CIRCULATION_ITEM_LOCATION_RETRIEVER'
    ] = lambda x: 'pickup_location_pid'

    loan_pid = loan_pid_fetcher(loan.id, loan)

    res, payload = _post(app, json_headers, params,
                         pid_value=loan_pid.pid_value, action='next')
    assert res.status_code == 202
    assert payload['metadata']['state'] == 'ITEM_AT_DESK'


def test_rest_loan_invalid_action(
    app, json_headers, params, mock_is_item_available_for_checkout,
    loan_created
):
    """Test API invalid action on loan."""
    loan = current_circulation.circulation.trigger(
        loan_created,
        **dict(params, trigger='request',
               pickup_location_pid='pickup_location_pid')
    )
    db.session.commit()
    assert loan['state'] == 'PENDING'

    loan_pid = loan_pid_fetcher(loan.id, loan)

    res, payload = _post(app, json_headers, params,
                         pid_value=loan_pid.pid_value, action='extend')
    assert res.status_code == 400
    assert 'message' in payload
