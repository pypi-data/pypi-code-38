# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for loan states."""
import copy
from datetime import timedelta

import pytest
from flask import current_app
from flask_security import login_user

from invenio_circulation.api import Loan, is_item_available_for_checkout
from invenio_circulation.errors import ItemDoNotMatchError, \
    ItemNotAvailableError, LoanMaxExtensionError, \
    NoValidTransitionAvailableError, RecordCannotBeRequestedError, \
    TransitionConstraintsViolationError
from invenio_circulation.proxies import current_circulation
from invenio_circulation.utils import parse_date

from .helpers import SwappedConfig, SwappedNestedConfig


def test_loan_checkout_checkin(
    mock_get_pending_loans_by_doc_pid, loan_created, db, params,
    mock_is_item_available_for_checkout
):
    """Test loan checkout and checkin actions."""

    mock_get_pending_loans_by_doc_pid.return_value = []
    mock_is_item_available_for_checkout.return_value = True
    assert loan_created["state"] == "CREATED"

    loan = current_circulation.circulation.trigger(
        loan_created, **dict(params, trigger="checkout")
    )
    db.session.commit()
    assert loan["state"] == "ITEM_ON_LOAN"

    # set same transaction location to avoid "in transit"
    same_location = params["transaction_location_pid"]
    with SwappedConfig(
        "CIRCULATION_ITEM_LOCATION_RETRIEVER", lambda x: same_location
    ):
        loan = current_circulation.circulation.trigger(loan, **dict(params))
        db.session.commit()
        assert loan["state"] == "ITEM_RETURNED"


def test_can_change_item_and_loc_pid_before_checkout(
    mock_get_pending_loans_by_doc_pid, loan_created, db, params,
    mock_is_item_available_for_checkout
):
    """Test that item pid can be changed before the item is on loan."""

    mock_get_pending_loans_by_doc_pid.return_value = []
    mock_is_item_available_for_checkout.return_value = True
    item_pid = params['item_pid']
    del params['item_pid']

    # auto assign both available item pid and the location corresponding to it
    with SwappedConfig(
        "CIRCULATION_ITEMS_RETRIEVER_FROM_DOCUMENT", lambda x: [item_pid]
    ):
        with SwappedConfig(
            "CIRCULATION_ITEM_LOCATION_RETRIEVER",
            lambda x: "pickup_location_pid"
        ):
            loan = current_circulation.circulation.trigger(
                loan_created, **dict(params, trigger="request")
            )

    db.session.commit()
    assert loan["state"] == "PENDING"
    assert loan["pickup_location_pid"] == "pickup_location_pid"
    assert loan["item_pid"] == "item_pid"

    with SwappedConfig(
        "CIRCULATION_ITEM_LOCATION_RETRIEVER", lambda x: "pickup_location_pid"
    ):
        changed_loan = copy.deepcopy(loan)
        changed_loan = current_circulation.circulation.trigger(
            changed_loan,
            **dict(params, trigger="next", item_pid="other_item_pid_1",
                   pickup_location_pid="other_location_pid_1"))
        db.session.commit()
        assert changed_loan["state"] == "ITEM_IN_TRANSIT_FOR_PICKUP"
        assert changed_loan["item_pid"] == "other_item_pid_1"
        assert changed_loan["pickup_location_pid"] == "other_location_pid_1"

        changed_loan = copy.deepcopy(loan)
        changed_loan = current_circulation.circulation.trigger(
            changed_loan,
            **dict(params, trigger="next", item_pid="other_item_pid_2"))
        db.session.commit()
        assert changed_loan["state"] == "ITEM_AT_DESK"
        assert changed_loan["item_pid"] == "other_item_pid_2"
        assert changed_loan["pickup_location_pid"] == "pickup_location_pid"

        changed_loan = copy.deepcopy(loan)
        changed_loan = current_circulation.circulation.trigger(
            changed_loan,
            **dict(params, trigger="checkout", item_pid="other_item_pid_3",
                   pickup_location_pid="other_location_pid_3"))
        db.session.commit()
        assert changed_loan["state"] == "ITEM_ON_LOAN"
        assert changed_loan["item_pid"] == "other_item_pid_3"
        assert changed_loan["pickup_location_pid"] == "other_location_pid_3"


# def test_assignment_of_pickup_location_pid

def test_cannot_change_item_pid_after_checkout(
    mock_get_pending_loans_by_doc_pid, loan_created, db, params,
    mock_is_item_available_for_checkout
):
    """Test that item pid cannot be changed after the item is on loan."""
    mock_get_pending_loans_by_doc_pid.return_value = []
    mock_is_item_available_for_checkout.return_value = True
    del params['item_pid']

    # auto assign both available item pid and the location corresponding to it

    with SwappedConfig(
        "CIRCULATION_ITEM_LOCATION_RETRIEVER",
        lambda x: "pickup_location_pid"
    ):
        loan = current_circulation.circulation.trigger(
            loan_created, **dict(params, trigger="checkout",
                                 item_pid="item_pid")
        )

    db.session.commit()
    assert loan["state"] == "ITEM_ON_LOAN"
    assert loan["item_pid"] == "item_pid"
    assert loan["pickup_location_pid"] == "pickup_location_pid"

    with SwappedConfig(
        "CIRCULATION_ITEM_LOCATION_RETRIEVER", lambda x: "pickup_location_pid"
    ):
        changed_loan = copy.deepcopy(loan)
        with pytest.raises(ItemDoNotMatchError):
            current_circulation.circulation.trigger(
                changed_loan,
                **dict(params, trigger="next", item_pid="other_item_pid_1"))

        changed_loan = copy.deepcopy(loan)
        with pytest.raises(ItemDoNotMatchError):
            current_circulation.circulation.trigger(
                changed_loan,
                **dict(params, trigger="extend", item_pid="other_item_pid_2"))

        changed_loan = copy.deepcopy(loan)
        with pytest.raises(ItemDoNotMatchError):
            current_circulation.circulation.trigger(
                changed_loan,
                **dict(params, trigger="cancel", item_pid="other_item_pid_3"))


def test_loan_extend(loan_created, db, params,
                     mock_ensure_item_is_available_for_checkout):
    """Test loan extend action."""

    mock_ensure_item_is_available_for_checkout.side_effect = None

    loan = current_circulation.circulation.trigger(
        loan_created, **dict(params, trigger="checkout")
    )
    db.session.commit()
    end_date = parse_date(loan["end_date"])

    def get_max_count_0(loan):
        return 0

    current_app.config["CIRCULATION_POLICIES"]["extension"][
        "max_count"
    ] = get_max_count_0

    with pytest.raises(LoanMaxExtensionError):
        loan = current_circulation.circulation.trigger(
            loan, **dict(params, trigger="extend")
        )

    def get_max_count_2(loan):
        return 2

    current_app.config["CIRCULATION_POLICIES"]["extension"][
        "max_count"
    ] = get_max_count_2

    loan = current_circulation.circulation.trigger(
        loan, **dict(params, trigger="extend")
    )
    db.session.commit()
    new_end_date = parse_date(loan["end_date"])
    assert new_end_date == end_date + timedelta(days=30)
    assert loan["extension_count"] == 1

    loan = current_circulation.circulation.trigger(
        loan, **dict(params, trigger="extend")
    )
    db.session.commit()

    # test too many extensions
    with pytest.raises(LoanMaxExtensionError):
        loan = current_circulation.circulation.trigger(
            loan, **dict(params, trigger="extend")
        )


def test_loan_extend_from_enddate(
    loan_created, db, params, mock_ensure_item_is_available_for_checkout
):
    """Test loan extend action from transaction date."""

    mock_ensure_item_is_available_for_checkout.side_effect = None

    loan = current_circulation.circulation.trigger(
        loan_created, **dict(params, trigger="checkout")
    )
    db.session.commit()
    extension_date = parse_date(loan.get("transaction_date"))
    current_app.config["CIRCULATION_POLICIES"]["extension"][
        "from_end_date"
    ] = False

    loan = current_circulation.circulation.trigger(
        loan, **dict(params, trigger="extend")
    )
    db.session.commit()
    new_end_date = parse_date(loan["end_date"])
    assert new_end_date == extension_date + timedelta(days=30)
    assert loan["extension_count"] == 1


def test_cancel_action(loan_created, db, params,
                       mock_ensure_item_is_available_for_checkout):
    """Test should pass when calling `cancel` from `ITEM_ON_LOAN`."""

    mock_ensure_item_is_available_for_checkout.side_effect = None

    loan = current_circulation.circulation.trigger(
        loan_created, **dict(params, trigger="checkout")
    )
    db.session.commit()

    loan = current_circulation.circulation.trigger(
        loan, **dict(params, trigger="cancel")
    )
    assert loan["state"] == "CANCELLED"


def test_cancel_fail(loan_created, params):
    """Test should fail when calling `cancel` from `CREATED`."""
    with pytest.raises(NoValidTransitionAvailableError):
        current_circulation.circulation.trigger(
            loan_created, **dict(params, trigger="cancel")
        )


def test_validate_item_in_transit_for_pickup(loan_created, db, params):
    """."""
    loan = current_circulation.circulation.trigger(
        loan_created,
        **dict(
            params,
            trigger="request",
            pickup_location_pid="pickup_location_pid",
        )
    )
    db.session.commit()
    assert loan["state"] == "PENDING"

    with SwappedConfig(
        "CIRCULATION_ITEM_LOCATION_RETRIEVER",
        lambda x: "external_location_pid",
    ):
        loan = current_circulation.circulation.trigger(loan, **dict(params))
        assert loan["state"] == "ITEM_IN_TRANSIT_FOR_PICKUP"


def test_checkout_start_is_transaction_date(
    loan_created, db, params, mock_ensure_item_is_available_for_checkout
):
    """Test checkout start date to transaction date when not set."""
    mock_ensure_item_is_available_for_checkout.side_effect = None

    number_of_days = 10

    with SwappedNestedConfig(
        ["CIRCULATION_POLICIES", "checkout", "duration_default"],
        lambda x: number_of_days,
    ):
        loan = current_circulation.circulation.trigger(
            loan_created, **dict(params, trigger="checkout")
        )
        db.session.commit()

        assert loan["state"] == "ITEM_ON_LOAN"
        assert loan["start_date"] == loan["transaction_date"]
        start_date = parse_date(loan["start_date"])
        end_date = start_date + timedelta(number_of_days)
        assert loan["end_date"] == end_date.isoformat()


def test_checkout_with_input_start_end_dates(
    loan_created, db, params, mock_ensure_item_is_available_for_checkout
):
    """Test checkout start and end dates are set as input."""

    mock_ensure_item_is_available_for_checkout.side_effect = None

    start_date = "2018-02-01T09:30:00+02:00"
    end_date = "2018-02-10T09:30:00+02:00"
    loan = current_circulation.circulation.trigger(
        loan_created,
        **dict(
            params,
            start_date=start_date,
            end_date=end_date,
            trigger="checkout",
        )
    )
    db.session.commit()
    assert loan["state"] == "ITEM_ON_LOAN"
    assert loan["start_date"] == start_date
    assert loan["end_date"] == end_date


def test_checkout_fails_when_wrong_dates(
    loan_created, params, mock_ensure_item_is_available_for_checkout
):
    """Test checkout fails when wrong input dates."""

    mock_ensure_item_is_available_for_checkout.side_effect = None

    with pytest.raises(ValueError):
        current_circulation.circulation.trigger(
            loan_created,
            **dict(
                params,
                start_date="2018-xx",
                end_date="2018-xx",
                trigger="checkout",
            )
        )


def test_checkout_fails_when_duration_invalid(
    loan_created, params, mock_ensure_item_is_available_for_checkout
):
    """Test checkout fails when wrong max duration."""

    mock_ensure_item_is_available_for_checkout.side_effect = None

    with pytest.raises(TransitionConstraintsViolationError):
        with SwappedNestedConfig(
            ["CIRCULATION_POLICIES", "checkout", "duration_validate"],
            lambda x: False,
        ):
            current_circulation.circulation.trigger(
                loan_created,
                **dict(
                    params,
                    start_date="2018-02-01T09:30:00+02:00",
                    end_date="2018-04-10T09:30:00+02:00",
                    trigger="checkout",
                )
            )


def test_checkin_end_date_is_transaction_date(
    mock_get_pending_loans_by_doc_pid,
    mock_ensure_item_is_available_for_checkout,
    loan_created, db, params
):
    """Test date the checkin date is the transaction date."""
    mock_get_pending_loans_by_doc_pid.return_value = []
    mock_ensure_item_is_available_for_checkout.side_effect = None
    loan = current_circulation.circulation.trigger(
        loan_created,
        **dict(
            params,
            start_date="2018-02-01T09:30:00+02:00",
            end_date="2018-02-10T09:30:00+02:00",
            trigger="checkout",
        )
    )
    db.session.commit()
    assert loan["state"] == "ITEM_ON_LOAN"

    same_location = params["transaction_location_pid"]
    with SwappedConfig(
        "CIRCULATION_ITEM_LOCATION_RETRIEVER", lambda x: same_location
    ):
        params["transaction_date"] = "2018-03-11T19:15:00+02:00"
        loan = current_circulation.circulation.trigger(loan, **dict(params))
        assert loan["state"] == "ITEM_RETURNED"
        assert loan["end_date"] == params["transaction_date"]


def test_item_availability(indexed_loans):
    """Test item_availability with various conditions."""
    assert is_item_available_for_checkout(item_pid="item_pending_1")
    assert not is_item_available_for_checkout(item_pid="item_on_loan_2")
    assert is_item_available_for_checkout(item_pid="item_returned_3")
    assert not is_item_available_for_checkout(item_pid="item_in_transit_4")
    assert not is_item_available_for_checkout(item_pid="item_at_desk_5")
    assert not is_item_available_for_checkout(
        item_pid="item_pending_on_loan_6")
    assert is_item_available_for_checkout(item_pid="item_returned_6")
    assert is_item_available_for_checkout(item_pid="no_loan")


def test_checkout_item_unavailable_steps(
    loan_created, db, params, users, app
):
    """Test checkout attempt on unavailable item."""
    user = users['manager']
    login_user(user)
    with pytest.raises(NoValidTransitionAvailableError):
        # loan created
        current_circulation.circulation.trigger(
            loan_created, **dict(params, trigger="request")
        )
        # loan pending
        current_circulation.circulation.trigger(
            loan_created, **dict(params, trigger="next")
        )
        loan_created["state"] = "ITEM_ON_LOAN"
        current_circulation.circulation.trigger(loan_created, **dict(params))

        # trying to checkout item already on loan
        current_circulation.circulation.trigger(
            loan_created, **dict(params, trigger="checkout")
        )


def test_deny_request(loan_created, params):
    """Test deny request action."""
    with SwappedNestedConfig(
        ["CIRCULATION_POLICIES", "request", "can_be_requested"],
        lambda x: False,
    ):
        with pytest.raises(RecordCannotBeRequestedError):
            current_circulation.circulation.trigger(
                loan_created,
                **dict(
                    params,
                    trigger="request",
                    pickup_location_pid="pickup_location_pid",
                )
            )
