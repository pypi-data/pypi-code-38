# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio Circulation base transitions."""

import copy
from datetime import datetime

from flask import current_app
from invenio_db import db

from ..api import is_item_available_for_checkout
from ..errors import DocumentDoNotMatchError, DocumentNotAvailableError, \
    InvalidLoanStateError, InvalidPermissionError, ItemNotAvailableError, \
    MissingRequiredParameterError, TransitionConditionsFailedError, \
    TransitionConstraintsViolationError
from ..proxies import current_circulation
from ..signals import loan_state_changed
from ..utils import parse_date


def ensure_same_patron(f):
    """Validate that the patron PID exists and cannot be changed."""
    def inner(self, loan, **kwargs):
        new_patron_pid = kwargs.get('patron_pid')

        if not current_app.config['CIRCULATION_PATRON_EXISTS'](new_patron_pid):
            msg = "Patron '{0}' not found in the system".format(new_patron_pid)
            raise TransitionConstraintsViolationError(description=msg)

        if 'patron_pid' in loan and new_patron_pid != loan['patron_pid']:
            msg = "Loan patron is '{0}' but transition is trying to set it " \
                  "to '{1}'".format(loan['patron_pid'], new_patron_pid)
            raise TransitionConstraintsViolationError(description=msg)

        return f(self, loan, **kwargs)
    return inner


def ensure_same_document(f):
    """Validate that the document PID exists and cannot be changed."""
    def inner(self, loan, **kwargs):
        new_document_pid = kwargs.get('document_pid')

        if not current_app \
                .config['CIRCULATION_DOCUMENT_EXISTS'](new_document_pid):
            msg = "Document '{0}' not found in the system"\
                .format(new_document_pid)
            raise DocumentNotAvailableError(description=msg)

        if loan.get('document_pid') \
           and new_document_pid != loan['document_pid']:
            msg = "Loan document is '{0}' but transition is trying to set" \
                  " it to '{1}'".format(loan['document_pid'],
                                        new_document_pid)
            raise DocumentDoNotMatchError(description=msg)

        return f(self, loan, **kwargs)
    return inner


def ensure_required_params(f):
    """Decorate to ensure that all required parameters has been passed."""
    def inner(self, loan, **kwargs):
        missing = [p for p in self.REQUIRED_PARAMS if p not in kwargs]
        if missing:
            msg = "Required input parameters are missing '[{}]'" \
                .format(missing)
            raise MissingRequiredParameterError(description=msg)
        if all(param not in kwargs for param in self.PARTIAL_REQUIRED_PARAMS):
            msg = "One of the parameters '[{}]' must be passed."\
                .format(self.PARTIAL_REQUIRED_PARAMS)
            raise MissingRequiredParameterError(description=msg)
        return f(self, loan, **kwargs)
    return inner


def check_trigger(f):
    """Decorate to check the transition should be manually triggered."""
    def inner(self, loan, **kwargs):
        if kwargs.get('trigger', 'next') != self.trigger:
            msg = "No param 'trigger' with value '{0}'.".format(self.trigger)
            raise TransitionConditionsFailedError(description=msg)
        return f(self, loan, **kwargs)
    return inner


class Transition(object):
    """A transition object that is triggered on conditions."""

    REQUIRED_PARAMS = [
        'transaction_user_pid',
        'patron_pid',
        'transaction_location_pid',
        'transaction_date'
    ]

    PARTIAL_REQUIRED_PARAMS = [
        'item_pid',
        'document_pid'
    ]

    def __init__(self, src, dest, trigger='next', permission_factory=None,
                 **kwargs):
        """Init transition object."""
        self.src = src
        self.dest = dest
        self.trigger = trigger
        self.permission_factory = permission_factory or current_app.config[
            'CIRCULATION_LOAN_TRANSITIONS_DEFAULT_PERMISSION_FACTORY']
        self.validate_transition_states()

    def ensure_item_is_available_for_checkout(self, loan):
        """Validate that an item is available."""
        if 'item_pid' not in loan:
            msg = "Item not set for loan with pid '{}'".format(loan.id)
            raise TransitionConstraintsViolationError(description=msg)

        if not current_app.config['CIRCULATION_ITEM_EXISTS'](loan['item_pid']):
            msg = "Item '{0}' not found in catalog".format(loan['item_pid'])
            raise ItemNotAvailableError(description=msg)

        if not is_item_available_for_checkout(loan['item_pid']):
            raise ItemNotAvailableError(
                item_pid=loan['item_pid'], transition=self.dest
            )

    def validate_transition_states(self):
        """Ensure that source and destination states are valid."""
        states = current_app.config['CIRCULATION_LOAN_TRANSITIONS'].keys()
        if not all([self.src in states, self.dest in states]):
            msg = "Source state '{0}' or destination state '{1}' not in [{2}]"\
                .format(self.src, self.dest, states)
            raise InvalidLoanStateError(description=msg)

    @check_trigger
    @ensure_required_params
    @ensure_same_patron
    @ensure_same_document
    def before(self, loan, **kwargs):
        """Validate input, evaluate conditions and raise if failed."""
        if self.permission_factory and not self.permission_factory(loan).can():
            raise InvalidPermissionError(
                permission=self.permission_factory(loan)
            )

        kwargs.setdefault('transaction_date', datetime.now())
        kwargs['transaction_date'] = parse_date(kwargs['transaction_date'])
        self.prev_loan = copy.deepcopy(loan)
        loan.update(kwargs)

    def execute(self, loan, **kwargs):
        """Execute before actions, transition and after actions."""
        self.before(loan, **kwargs)
        loan['state'] = self.dest
        self.after(loan)

    def after(self, loan):
        """Commit record and index."""
        loan['transaction_date'] = loan['transaction_date'].isoformat()
        loan.commit()
        db.session.commit()
        current_circulation.loan_indexer.index(loan)

        loan_state_changed.send(
            self, prev_loan=self.prev_loan, loan=loan, trigger=self.trigger)
