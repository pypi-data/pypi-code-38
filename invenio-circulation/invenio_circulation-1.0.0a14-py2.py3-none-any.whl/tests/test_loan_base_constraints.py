# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for loan mandatory constraints."""

import pytest

from invenio_circulation.errors import ItemDoNotMatchError, \
    ItemNotAvailableError, MissingRequiredParameterError, \
    TransitionConstraintsViolationError
from invenio_circulation.pidstore.fetchers import loan_pid_fetcher
from invenio_circulation.proxies import current_circulation

from .helpers import SwappedConfig


def test_should_fail_when_missing_required_params(loan_created):
    """Test that transition fails when there required params are missing."""
    with pytest.raises(MissingRequiredParameterError):
        current_circulation.circulation.trigger(
            loan_created, **dict(patron_pid="pid", trigger="checkout")
        )


def test_should_fail_when_item_not_exist(loan_created, params):
    """Test that transition fails when loan item do not exists."""
    with pytest.raises(ItemNotAvailableError):
        with SwappedConfig("CIRCULATION_ITEM_EXISTS", lambda x: False):
            current_circulation.circulation.trigger(
                loan_created, **dict(params, trigger="checkout")
            )


def test_should_fail_when_item_is_changed(
    loan_created, db, params
):
    """Test that constraints fail if item for an existing loan is changed."""
    with SwappedConfig(
        "CIRCULATION_ITEM_LOCATION_RETRIEVER", lambda x: "pickup_location_pid"
    ):
        loan = current_circulation.circulation.trigger(
            loan_created, **dict(params, trigger="checkout")
        )
    db.session.commit()

    params["item_pid"] = "different_item_pid"
    with pytest.raises(ItemDoNotMatchError):
        current_circulation.circulation.trigger(loan, **dict(params))


def test_should_fail_when_patron_not_exist(loan_created, params):
    """Test that transition fails when loan patron do not exists."""
    with pytest.raises(TransitionConstraintsViolationError):
        with SwappedConfig("CIRCULATION_PATRON_EXISTS", lambda x: False):
            current_circulation.circulation.trigger(
                loan_created, **dict(params, trigger="checkout")
            )


def test_should_fail_when_patron_is_changed(
    loan_created, db, params
):
    """Test that constraints fail if patron for an existing loan is changed."""
    with SwappedConfig(
        "CIRCULATION_ITEM_LOCATION_RETRIEVER", lambda x: "pickup_location_pid"
    ):
        loan = current_circulation.circulation.trigger(
            loan_created, **dict(params, trigger="request")
        )
    db.session.commit()

    params["patron_pid"] = "different_patron_pid"
    with pytest.raises(TransitionConstraintsViolationError):
        current_circulation.circulation.trigger(loan, **dict(params))


def test_persist_loan_parameters(
    loan_created, db, params, mock_ensure_item_is_available_for_checkout
):
    """Test that input params are correctly persisted."""
    mock_ensure_item_is_available_for_checkout.side_effect = None

    loan_pid = loan_pid_fetcher(loan_created.id, loan_created)
    with SwappedConfig(
        "CIRCULATION_ITEM_LOCATION_RETRIEVER", lambda x: "pickup_location_pid"
    ):
        loan = current_circulation.circulation.trigger(
            loan_created, **dict(params, trigger="checkout")
        )
    db.session.commit()

    params["loan_pid"] = loan_pid.pid_value
    params["state"] = "ITEM_ON_LOAN"
    params["start_date"] = loan["start_date"]
    params["end_date"] = loan["end_date"]
    params["trigger"] = loan["trigger"]
    params["pickup_location_pid"] = loan["pickup_location_pid"]
    params["item"] = {"ref": "6"}
    params["$schema"] = "https://localhost:5000/schema/loans/loan-v1.0.0.json"
    assert loan == params
