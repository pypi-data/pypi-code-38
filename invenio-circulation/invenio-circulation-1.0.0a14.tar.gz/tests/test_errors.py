# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Excpetions tests."""

import pytest

from invenio_circulation.errors import InvalidLoanStateError, \
    InvalidPermissionError, ItemNotAvailableError, LoanMaxExtensionError, \
    MissingRequiredParameterError, MultipleLoansOnItemError, \
    NotImplementedConfigurationError, NoValidTransitionAvailableError, \
    RecordCannotBeRequestedError, TransitionConditionsFailedError, \
    TransitionConstraintsViolationError


def test_not_implemented(app):
    """Test NotImplementedConfigurationError."""
    config_variable = 'CONFIG_VAR'
    msg = (
        "Function is not implemented. Implement this function in your module "
        "and pass it to the config variable '{}'".format(config_variable)
    )
    with pytest.raises(NotImplementedConfigurationError) as ex:
        raise NotImplementedConfigurationError(config_variable="CONFIG_VAR")
    assert ex.value.code == 400
    assert ex.value.description == msg


def test_invalid_permission(app):
    """Test InvalidPermissionError."""
    permission = 'simple_user'
    msg = "This action is not permitted for your role '{}'".format(permission)
    with pytest.raises(InvalidPermissionError) as ex:
        raise InvalidPermissionError(permission=permission)
    assert ex.value.code == 403
    assert ex.value.description == msg


def test_record_cannot_be_requested(app):
    """Test record cannot be requested."""
    state = 'loan_state'
    item_pid = 'item_pid'
    msg = (
        'Transition to {0} failed.'
        'Document {1} can not be requested.'
    ).format(state, item_pid)

    with pytest.raises(RecordCannotBeRequestedError) as ex:
        raise RecordCannotBeRequestedError(description=msg)
    assert ex.value.code == 400
    assert ex.value.description == msg


def test_item_not_available(app):
    """Test item not available."""
    item_pid = "1"
    transition = "checkout"
    msg = (
        "The item requested with pid '{0}' is not available. "
        "Transition to '{1}' has failed.".format(item_pid, transition)
    )
    with pytest.raises(ItemNotAvailableError) as ex:
        raise ItemNotAvailableError(item_pid=item_pid, transition=transition)

    assert ex.value.code == 400
    assert ex.value.description == msg


def test_multiple_loans_on_item(app):
    """Test multiple loans on item."""
    item_pid = "1"
    msg = "Multiple active loans on item with pid '{}'".format(item_pid)
    with pytest.raises(MultipleLoansOnItemError) as ex:
        raise MultipleLoansOnItemError(item_pid=item_pid)

    assert ex.value.code == 400
    assert ex.value.description == msg


def test_invalid_loan_state(app):
    """Test invalid loan state."""
    state = "not_valid"
    msg = "Invalid loan state '{}'".format(state)
    with pytest.raises(InvalidLoanStateError) as ex:
        raise InvalidLoanStateError(state=state)
    assert ex.value.code == 400
    assert ex.value.description == msg


def test_no_valid_transitions_available(app):
    """Test no valid transitions available."""
    loan_pid = 'loan_pid'
    state = "not_valid"
    msg = (
        "For the loan with pid '{0}' there are no valid transitions from "
        "its current state '{1}'".format(loan_pid, state)
    )
    with pytest.raises(NoValidTransitionAvailableError) as ex:
        raise NoValidTransitionAvailableError(loan_pid=loan_pid, state=state)
    assert ex.value.code == 400
    assert ex.value.description == msg


def test_transition_conditions_failed(app):
    """Test transition conditions fail."""
    msg = "Transition conditions have failed."

    with pytest.raises(TransitionConditionsFailedError) as ex:
        raise TransitionConditionsFailedError(description=msg)
    assert ex.value.code == 400
    assert ex.value.description == msg


def test_transition_constraints_violation(app):
    """Test transition constraints violation."""
    msg = "The contraints of the transitions have been wildely violated."
    with pytest.raises(TransitionConstraintsViolationError) as ex:
        raise TransitionConstraintsViolationError(description=msg)
    assert ex.value.code == 400
    assert ex.value.description == msg


def test_missing_property(app):
    """Test missing property."""
    msg = "The property pid is missing."
    with pytest.raises(MissingRequiredParameterError) as ex:
        raise MissingRequiredParameterError(description=msg)
    assert ex.value.code == 400
    assert ex.value.description == msg


def test_loan_max_extensions(app):
    """Test loan max extension error."""
    loan_pid = "loan_pid"
    extension_count = 42
    msg = (
        "You have reached the maximum amount of extesions '{}' "
        "for loan '{}'".format(extension_count, loan_pid)
    )
    with pytest.raises(LoanMaxExtensionError) as ex:
        raise LoanMaxExtensionError(
            loan_pid=loan_pid,
            extension_count=extension_count
        )
    assert ex.value.code == 400
    assert ex.value.description == msg
