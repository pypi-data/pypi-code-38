# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for circulation signals."""

from invenio_circulation.proxies import current_circulation
from invenio_circulation.signals import loan_state_changed


def test_signals_loan_request(loan_created, db, params):
    """Test signal for loan request action."""
    recorded = []

    def record_signals(_, prev_loan, loan, trigger):
        recorded.append((prev_loan, loan, trigger))

    loan_state_changed.connect(record_signals, weak=False)

    assert len(recorded) == 0
    current_circulation.circulation.trigger(
        loan_created,
        **dict(
            params,
            trigger="request",
            pickup_location_pid="pickup_location_pid",
        )
    )
    db.session.commit()
    assert len(recorded) == 1
    prev_loan, updated_loan, trigger = recorded.pop()
    assert prev_loan["state"] == "CREATED"
    assert updated_loan["state"] == "PENDING"
    assert trigger == "request"


def test_signals_loan_extend(loan_created, db, params):
    """Test signals for loan extend action."""
    recorded = []

    def record_signals(_, prev_loan, loan, trigger):
        recorded.append((prev_loan, loan, trigger))

    loan_state_changed.connect(record_signals, weak=False)

    assert len(recorded) == 0
    loan = current_circulation.circulation.trigger(
        loan_created, **dict(params, trigger="checkout")
    )
    db.session.commit()
    assert len(recorded) == 1
    prev_loan, updated_loan, trigger = recorded.pop()
    assert prev_loan["state"] == "CREATED"
    assert updated_loan["state"] == "ITEM_ON_LOAN"
    assert trigger == "checkout"

    current_circulation.circulation.trigger(
        loan, **dict(params, trigger="extend")
    )
    db.session.commit()
    assert len(recorded) == 1
    prev_loan, updated_loan, trigger = recorded.pop()
    assert prev_loan["state"] == "ITEM_ON_LOAN"
    assert updated_loan["state"] == "ITEM_ON_LOAN"
    assert prev_loan["end_date"] != updated_loan["end_date"]
    assert trigger == "extend"
