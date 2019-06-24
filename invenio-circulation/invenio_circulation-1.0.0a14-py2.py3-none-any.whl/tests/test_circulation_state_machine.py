# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for circulation state machine logic."""

import pytest

from invenio_circulation.errors import NoValidTransitionAvailableError
from invenio_circulation.proxies import current_circulation


def test_invalid_transitions(loan_created, app, params):
    """Test that there are no conditional transitions at this state."""
    with pytest.raises(NoValidTransitionAvailableError):
        current_circulation.circulation.trigger(loan_created, **params)
