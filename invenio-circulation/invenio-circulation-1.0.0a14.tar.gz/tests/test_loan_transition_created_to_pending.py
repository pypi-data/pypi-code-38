# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for loan states."""

from invenio_circulation.api import Loan
from invenio_circulation.proxies import current_circulation

from .helpers import SwappedConfig


def test_loan_request_on_document_with_auto_available_item_assignment(
    loan_created, db, params,
    mock_is_item_available_for_checkout
):
    """Test loan request on document with auto available item assignment."""
    mock_is_item_available_for_checkout.return_value = True

    # we have a request just on document_pid
    del params['item_pid']

    # mock functions for automatically assigning an available item
    # and a default pickup location
    with SwappedConfig(
        "CIRCULATION_ITEMS_RETRIEVER_FROM_DOCUMENT", lambda x: ["other_pid"]
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
    assert loan["item_pid"] == "other_pid"


def test_loan_request_on_available_item_requested_location(
    loan_created, db, params
):
    """Test loan request action on available item with pickup override."""

    with SwappedConfig(
        "CIRCULATION_ITEM_LOCATION_RETRIEVER",
        lambda x: "pickup_location_pid"
    ):
        loan = current_circulation.circulation.trigger(
            loan_created,
            **dict(
                params,
                trigger="request",
                pickup_location_pid="other_location_pid",
            )
        )
    db.session.commit()
    assert loan["state"] == "PENDING"
    assert loan["pickup_location_pid"] == "other_location_pid"
    assert loan["item_pid"] == params["item_pid"]


def test_loan_request_on_available_item_default_location(
    loan_created, db, params
):
    """Test loan request action on available item without pickup override."""

    with SwappedConfig(
        "CIRCULATION_ITEM_LOCATION_RETRIEVER",
        lambda x: "pickup_location_pid"
    ):
        loan = current_circulation.circulation.trigger(
            loan_created,
            **dict(
                params,
                trigger="request",
            )
        )
    db.session.commit()
    assert loan["state"] == "PENDING"
    assert loan["pickup_location_pid"] == "pickup_location_pid"
    assert loan["item_pid"] == params["item_pid"]


def test_loan_request_on_document_with_unavailable_items(
    loan_created, db, params,
    mock_is_item_available_for_checkout
):
    """Test loan request on a document that has no items available."""
    mock_is_item_available_for_checkout.return_value = False

    # we have a request just on document_pid
    del params['item_pid']

    # find an item attached to the document, which will be unavailable
    with SwappedConfig(
        "CIRCULATION_ITEMS_RETRIEVER_FROM_DOCUMENT", lambda x: ["item_pid"]
    ):
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
        assert "item_pid" not in loan
        assert loan["document_pid"] == "document_pid"
        assert loan["pickup_location_pid"] == "pickup_location_pid"


def test_auto_assignment_of_returned_item_to_pending_document_requests(
    loan_created, db, params,
    mock_is_item_available_for_checkout,
    mock_get_pending_loans_by_doc_pid
):
    """Test assignment of newly available items to pending doc requests."""
    mock_is_item_available_for_checkout.return_value = True
    mock_get_pending_loans_by_doc_pid.return_value = ["item_pid"]

    # find which document the returned item is associated to
    with SwappedConfig(
        "CIRCULATION_DOCUMENT_RETRIEVER_FROM_ITEM", lambda x: "document_pid"
    ):
        same_location = params["transaction_location_pid"]
        with SwappedConfig(
            "CIRCULATION_ITEM_LOCATION_RETRIEVER", lambda x: same_location
        ):
            # start a loan on item with pid 'item_pid'
            new_loan = current_circulation.circulation.trigger(
                loan_created,
                **dict(
                    params,
                    trigger="checkout",
                    item_pid="item_pid",
                    pickup_location_pid="pickup_location_pid",
                )
            )
            db.session.commit()
            assert new_loan["state"] == "ITEM_ON_LOAN"

            # create a new loan request on document_pid without items available
            new_loan_created = Loan.create({
                Loan.pid_field: "2"
            })
            # remove item_pid
            params.pop("item_pid")
            pending_loan = current_circulation.circulation.trigger(
                new_loan_created,
                **dict(
                    params,
                    trigger="request",
                    document_pid="document_pid",
                    pickup_location_pid="pickup_location_pid",
                )
            )
            db.session.commit()
            assert pending_loan["state"] == "PENDING"
            # no item available found. Request is created with no item attached
            assert "item_pid" not in pending_loan
            assert pending_loan["document_pid"] == "document_pid"

            # resolve pending document requests to `document_pid`
            mock_get_pending_loans_by_doc_pid.return_value = [pending_loan]

            returned_loan = current_circulation.circulation.trigger(
                new_loan,
                **dict(
                    params,
                    item_pid="item_pid",
                    pickup_location_pid="pickup_location_pid",
                )
            )
            db.session.commit()
            assert returned_loan["state"] == "ITEM_RETURNED"

            # item `item_pid` has been attached to pending loan request on
            # `document_pid` automatically
            assert pending_loan["state"] == "PENDING"
            assert pending_loan["item_pid"] == "item_pid"
            assert pending_loan["document_pid"] == "document_pid"
