# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for loan states."""

import pytest

from invenio_circulation.errors import TransitionConstraintsViolationError
from invenio_circulation.proxies import current_circulation

from .helpers import SwappedConfig


def test_checkout_from_item_at_desk_valid_duration(loan_created, db, params):
    """Test transition from ITEM_AT_DESK to ITEM_ON_LOAN state."""
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
        "CIRCULATION_ITEM_LOCATION_RETRIEVER", lambda x: "pickup_location_pid"
    ):
        loan = current_circulation.circulation.trigger(
            loan, **dict(params)
        )
        assert loan["state"] == "ITEM_AT_DESK"

        loan = current_circulation.circulation.trigger(
            loan, **dict(params)
        )

        assert loan["state"] == "ITEM_ON_LOAN"


def test_checkout_from_item_at_desk_invalid_duration(loan_created, db, params):
    """Test transition from ITEM_AT_DESK to ITEM_ON_LOAN state."""
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
        "CIRCULATION_ITEM_LOCATION_RETRIEVER", lambda x: "pickup_location_pid"
    ):
        loan = current_circulation.circulation.trigger(
            loan, **dict(params)
        )
        assert loan["state"] == "ITEM_AT_DESK"

        loan["start_date"] = "2018-01-01"
        loan["end_date"] = "2018-03-02"  # + 60 days

        with pytest.raises(TransitionConstraintsViolationError):
            current_circulation.circulation.trigger(
                loan, **dict(params)
            )
