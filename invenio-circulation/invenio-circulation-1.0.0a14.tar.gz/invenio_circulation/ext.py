# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module for the circulation of bibliographic items."""

from __future__ import absolute_import, print_function

from copy import deepcopy

from flask import current_app
from invenio_indexer.api import RecordIndexer
from invenio_records_rest.utils import obj_or_import_string
from werkzeug.utils import cached_property

from . import config
from .errors import InvalidLoanStateError, NoValidTransitionAvailableError, \
    TransitionConditionsFailedError
from .pidstore.pids import CIRCULATION_LOAN_PID_TYPE
from .search.api import LoansSearch
from .transitions.base import Transition


class InvenioCirculation(object):
    """Invenio-Circulation extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.app = app
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.config.setdefault("RECORDS_REST_ENDPOINTS", {})

        app.config["CIRCULATION_REST_ENDPOINTS"].setdefault("loanid", {})[
            "links_factory_imp"
        ] = app.config["CIRCULATION_LOAN_LINKS_FACTORY"]

        app.config["RECORDS_REST_ENDPOINTS"].update(
            app.config["CIRCULATION_REST_ENDPOINTS"]
        )
        app.extensions["invenio-circulation"] = self

    def init_config(self, app):
        """Initialize configuration."""
        app.config.setdefault(
            "CIRCULATION_ITEMS_RETRIEVER_FROM_DOCUMENT", lambda x: []
        )
        app.config.setdefault(
            "CIRCULATION_DOCUMENT_RETRIEVER_FROM_ITEM", lambda x: None
        )
        for k in dir(config):
            if k.startswith("CIRCULATION_"):
                app.config.setdefault(k, getattr(config, k))

    @cached_property
    def circulation(self):
        """Return the Circulation state machine."""
        return _Circulation(
            transitions_config=deepcopy(
                current_app.config["CIRCULATION_LOAN_TRANSITIONS"]
            )
        )

    def _get_endpoint_config(self):
        """Return endpoint configuration for circulation."""
        endpoints = self.app.config.get('CIRCULATION_REST_ENDPOINTS', [])
        pid_type = CIRCULATION_LOAN_PID_TYPE
        return endpoints.get(pid_type, {})

    @cached_property
    def loan_search(self):
        """Return the current Loan search instance."""
        circ_endpoint = self._get_endpoint_config()
        _cls = circ_endpoint.get('search_class', LoansSearch)
        return obj_or_import_string(_cls)()

    @cached_property
    def loan_indexer(self):
        """Return the current Loan indexer instance."""
        circ_endpoint = self._get_endpoint_config()
        _cls = circ_endpoint.get('indexer_class', RecordIndexer)
        return obj_or_import_string(_cls)()


class _Circulation(object):
    """Circulation state sachine."""

    def __init__(self, transitions_config):
        """Constructor."""
        self.transitions = {}
        for src_state, transitions in transitions_config.items():
            self.transitions.setdefault(src_state, [])
            for t in transitions:
                _cls = t.pop("transition", Transition)
                instance = _cls(**dict(t, src=src_state))
                self.transitions[src_state].append(instance)

    def _validate_current_state(self, state):
        """Validate that the given loan state is configured."""
        if not state or state not in self.transitions:
            raise InvalidLoanStateError(state=state)

    def trigger(self, loan, **kwargs):
        """Trigger the action to transit a Loan to the next state."""
        current_state = loan.get("state")
        self._validate_current_state(current_state)

        for t in self.transitions[current_state]:
            try:
                t.execute(loan, **kwargs)
                return loan
            except TransitionConditionsFailedError as ex:
                pass

        raise NoValidTransitionAvailableError(
            loan_pid=str(loan.id), state=current_state
        )
