# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Circulation views."""

from copy import deepcopy

from flask import Blueprint, current_app, jsonify, request, url_for
from invenio_db import db
from invenio_records_rest.utils import obj_or_import_string
from invenio_records_rest.views import pass_record
from invenio_rest import ContentNegotiatedMethodView

from .api import get_loan_for_item
from .errors import InvalidLoanStateError, ItemNotAvailableError, \
    MissingRequiredParameterError
from .permissions import need_permissions
from .pidstore.fetchers import loan_pid_fetcher
from .pidstore.pids import _LOANID_CONVERTER, CIRCULATION_LOAN_PID_TYPE
from .proxies import current_circulation
from .signals import loan_replace_item


def extract_transitions_from_app(app):
    """Return all possible actions for configured transitions."""
    transitions_config = app.config.get("CIRCULATION_LOAN_TRANSITIONS", {})
    distinct_actions = set()
    for src_state, transitions in transitions_config.items():
        for t in transitions:
            distinct_actions.add(t.get("trigger", "next"))
    return distinct_actions


def build_url_action_for_pid(pid, action):
    """Build urls for Loan actions."""
    return url_for(
        "invenio_circulation_loan_actions.{0}_actions".format(pid.pid_type),
        pid_value=pid.pid_value,
        action=action,
        _external=True,
    )


def create_loan_actions_blueprint(app):
    """Create a blueprint for Loan actions."""
    blueprint = Blueprint(
        "invenio_circulation_loan_actions", __name__, url_prefix=""
    )

    endpoints = app.config.get("CIRCULATION_REST_ENDPOINTS", [])
    pid_type = CIRCULATION_LOAN_PID_TYPE
    options = endpoints.get(pid_type, {})
    if options:
        options = deepcopy(options)
        serializers = {}
        if "record_serializers" in options:
            rec_serializers = options.get("record_serializers")
            serializers = {
                mime: obj_or_import_string(func)
                for mime, func in rec_serializers.items()
            }

        loan_actions = LoanActionResource.as_view(
            LoanActionResource.view_name.format(pid_type),
            serializers=serializers,
            ctx={},
        )

        distinct_actions = extract_transitions_from_app(app)
        url = "{0}/<any({1}):action>".format(
            options["item_route"], ",".join(distinct_actions)
        )

        blueprint.add_url_rule(url, view_func=loan_actions, methods=["POST"])

    return blueprint


class LoanActionResource(ContentNegotiatedMethodView):
    """Loan action resource."""

    view_name = "{0}_actions"

    def __init__(self, serializers, ctx, *args, **kwargs):
        """Constructor."""
        super(LoanActionResource, self).__init__(serializers, *args, **kwargs)
        for key, value in ctx.items():
            setattr(self, key, value)

    @need_permissions("loan-actions")
    @pass_record
    def post(self, pid, record, action, **kwargs):
        """Handle loan action."""
        params = request.get_json()
        record = current_circulation.circulation.trigger(
            record, **dict(params, trigger=action)
        )
        db.session.commit()
        return self.make_response(
            pid,
            record,
            202,
            links_factory=current_app.config.get(
                "CIRCULATION_LOAN_LINKS_FACTORY"
            ),
        )


def create_loan_for_item_blueprint(app):
    """Create a blueprint for Loan status of Items."""
    blueprint = Blueprint(
        "invenio_circulation_loan_for_item", __name__, url_prefix=""
    )

    rec_serializers = {
        "application/json": (
            "invenio_records_rest.serializers" ":json_v1_response"
        )
    }
    serializers = {
        mime: obj_or_import_string(func)
        for mime, func in rec_serializers.items()
    }

    loan_request = ItemLoanResource.as_view(
        ItemLoanResource.view_name, serializers=serializers, ctx={}
    )

    url = "circulation/items/<pid_value>/loan"

    blueprint.add_url_rule(url, view_func=loan_request, methods=["GET"])
    return blueprint


class ItemLoanResource(ContentNegotiatedMethodView):
    """Item circulation state resource."""

    view_name = "loan_resource"

    def __init__(self, serializers, ctx, *args, **kwargs):
        """Resource view constructor."""
        super(ItemLoanResource, self).__init__(serializers, *args, **kwargs)
        for key, value in ctx.items():
            setattr(self, key, value)

    @need_permissions("loan-read-access")
    def get(self, *args, **kwargs):
        """Handle GET request for item state."""
        item_pid = kwargs.get("pid_value", None)
        if not item_pid:
            raise ItemNotAvailableError(item_pid=item_pid)

        loan = get_loan_for_item(item_pid)
        if loan:
            loan_pid = loan_pid_fetcher(loan.id, loan)
            return self.make_response(
                loan_pid,
                loan,
                200,
                links_factory=current_app.config.get(
                    "CIRCULATION_LOAN_LINKS_FACTORY"
                ),
            )
        return jsonify({})


def create_loan_replace_item_blueprint(app):
    """Create a blueprint for replacing Loan Item."""
    blueprint = Blueprint(
        "invenio_circulation_loan_replace_item", __name__, url_prefix=""
    )

    rec_serializers = {
        "application/json": (
            "invenio_records_rest.serializers" ":json_v1_response"
        )
    }
    serializers = {
        mime: obj_or_import_string(func)
        for mime, func in rec_serializers.items()
    }
    replace_item_view = LoanReplaceItemResource.as_view(
        LoanReplaceItemResource.view_name.format(CIRCULATION_LOAN_PID_TYPE),
        serializers=serializers,
        ctx={},
    )

    url = "circulation/loans/<{0}:pid_value>/replace-item".format(
        _LOANID_CONVERTER
    )
    blueprint.add_url_rule(url, view_func=replace_item_view, methods=["POST"])
    return blueprint


def validate_replace_item(loan, data):
    """Validate data before replacing an item in loan."""
    active_states = current_app.config["CIRCULATION_STATES_LOAN_ACTIVE"]
    if loan["state"] not in active_states:
        raise InvalidLoanStateError(description=(
            "Cannot replace item in a loan that is not in active state. "
            "Current loan state '{}'".format(loan["state"])
        ))

    item_pid = data.get("item_pid")
    if not item_pid:
        raise MissingRequiredParameterError(
            description="Parameter item_pid is required."
        )

    item_exists = current_app.config.get("CIRCULATION_ITEM_EXISTS")(item_pid)
    if not item_exists:
        raise ItemNotAvailableError(item_pid=item_pid)


class LoanReplaceItemResource(ContentNegotiatedMethodView):
    """Loan update resource."""

    view_name = "loan_replace_item_resource"

    def __init__(self, serializers, ctx, *args, **kwargs):
        """Constructor."""
        super(LoanReplaceItemResource, self).__init__(
            serializers, *args, **kwargs
        )
        for key, value in ctx.items():
            setattr(self, key, value)

    @need_permissions("loan-actions")
    @pass_record
    def post(self, pid, record, *args, **kwargs):
        """Handle POST request to update loan with new item."""
        old_item_pid = record["item_pid"]
        data = request.get_json()
        validate_replace_item(record, data)
        record.update_item_ref(data)
        record.commit()
        db.session.commit()

        current_circulation.loan_indexer.index(record)
        if old_item_pid:
            loan_replace_item.send(
                self,
                old_item_pid=old_item_pid,
                new_item_pid=record["item_pid"]
            )

        return self.make_response(
            pid,
            record,
            202,
            links_factory=current_app.config.get(
                "CIRCULATION_LOAN_LINKS_FACTORY"
            ),
        )
