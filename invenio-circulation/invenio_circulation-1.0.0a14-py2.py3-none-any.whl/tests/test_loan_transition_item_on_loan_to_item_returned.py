# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for loan states."""

from invenio_circulation.proxies import current_circulation

from .helpers import SwappedConfig


def test_item_on_loan_to_item_in_transit_to_house(
    loan_created, db, params
):
    """Test transition from ITEM_ON_LOAN to ITEM_IN_TRANSIT_TO_HOUSE state."""
    loan = current_circulation.circulation.trigger(
        loan_created,
        **dict(
            params,
            trigger="checkout",
            pickup_location_pid="loc_pid",
        )
    )

    assert loan["state"] == "ITEM_ON_LOAN"
    assert loan["transaction_location_pid"] == "loc_pid"

    # item is not returned to the same location
    with SwappedConfig(
        "CIRCULATION_ITEM_LOCATION_RETRIEVER", lambda x: "other_location_pid"
    ):
        loan = current_circulation.circulation.trigger(
            loan, **dict(params)
        )

        assert loan["state"] == "ITEM_IN_TRANSIT_TO_HOUSE"


def test_item_on_loan_to_item_returned_same_location(
    loan_created, db, params
):
    """Test transition from ITEM_ON_LOAN to ITEM_RETURNED state."""
    loan = current_circulation.circulation.trigger(
        loan_created,
        **dict(
            params,
            trigger="checkout",
            pickup_location_pid="loc_pid",
        )
    )

    assert loan["state"] == "ITEM_ON_LOAN"
    assert loan["transaction_location_pid"] == "loc_pid"

    # item is returned to the same location
    with SwappedConfig(
        "CIRCULATION_ITEM_LOCATION_RETRIEVER", lambda x: "loc_pid"
    ):
        loan = current_circulation.circulation.trigger(
            loan, **dict(params)
        )
        assert loan["state"] == "ITEM_RETURNED"
