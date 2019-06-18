# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

import re
from collections import defaultdict

from tcell_agent.agent import TCellAgent
from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.policies.policy_types import PolicyTypes
from tcell_agent.policies.dataloss_policy import DataLossPolicy
from tcell_agent.events.dlp import DlpEvent
from tcell_agent.utils.compat import escape_html


class ContextFilter(object):
    DATABASE = "db"
    REQUEST = "request"

    def __init__(self):
        self.type = None
        self.rule = None
        self.context = None
        self.parameter = None
        self.database = None
        self.schema = None
        self.table = None
        self.field = None

    def for_request(self, context, parameter, rule):
        self.type = ContextFilter.REQUEST
        self.context = context
        self.parameter = parameter
        self.rule = rule
        return self

    def for_database(self, database, schema, table, field, rule):
        self.type = ContextFilter.DATABASE
        self.database = database
        self.schema = schema
        self.table = table
        self.field = field
        self.rule = rule
        return self

    def __hash__(self):
        return hash("{0},{1},{2},{3},{4},{5},{6},{7}".format(
            self.type,
            self.rule,
            self.parameter,
            self.database,
            self.schema,
            self.table,
            self.field,
            self.context
        ))


def validate_term(term):
    return term not in [
        None,
        "",
        DataLossPolicy.B_REDACT_MESSAGE,
        DataLossPolicy.REDACT_MESSAGE
    ] and len(str(term)) > 4


class TCellInstrumentationContext(object):
    def __init__(self):
        self.filter_from_body = set()
        self.filter_from_log = set()
        self.session_id = None
        self.user_id = None
        self.user_agent = None
        self.remote_address = None
        self.route_id = None
        self.path = None
        self.fullpath = None
        self.uri = None
        self.filters = defaultdict(set)
        self.start_time = 0
        self.ip_blocking_triggered = False
        self.appsensor_meta = AppSensorMeta()
        self.method = None
        self.referrer = None

    def add_response_db_filter(self, term, action_obj, database, schema, table, field):
        try:
            if not validate_term(term):
                return
            self.filters[re.escape(str(term))].add(ContextFilter().for_database(
                database, schema, table, field, action_obj))
        except Exception:
            pass

    def add_response_parameter_filter(self, term, action_obj, parameter_name):
        try:
            if not validate_term(term):
                return
            self.filters[re.escape(str(term))].add(ContextFilter().for_request("form", parameter_name, action_obj))
        except Exception:
            pass

    def add_response_cookie_filter(self, term, action_obj, parameter_name):
        try:
            if not validate_term(term):
                return
            self.filters[re.escape(str(term))].add(ContextFilter().for_request("cookie", parameter_name, action_obj))
        except Exception:
            pass

    def add_header_filter(self, term, action_obj, header_name):
        try:
            if not validate_term(term):
                return
            self.filters[re.escape(str(term))].add(ContextFilter().for_request("header", header_name, action_obj))
        except Exception:
            pass

    def add_response_body_filter(self, string):
        self.filter_from_body.add(string)
        self.filter_from_body.add(escape_html(string))

    def add_log_filter(self, string):
        self.filter_from_log.add(string)

    def filter_body(self, body):
        dataloss_policy = TCellAgent.get_policy(PolicyTypes.DATALOSS)
        if dataloss_policy and dataloss_policy.enabled:
            def filterx(body, replace, send, term):
                send_event_flags = {"send": False}

                def pythong_2_or_3_repl():
                    if not isinstance(body, str):
                        return DataLossPolicy.B_REDACT_MESSAGE
                    return DataLossPolicy.REDACT_MESSAGE

                def repl(found_term):
                    if replace:
                        send_event_flags["send"] = True
                        return pythong_2_or_3_repl()
                    if send:
                        send_event_flags["send"] = True
                    return found_term.group(0)

                if not isinstance(body, str) and isinstance(term, str):
                    encoded_term = term.encode("utf-8")
                else:
                    encoded_term = term
                try:
                    body = re.sub(encoded_term, repl, body)
                except Exception:
                    pass
                return (send_event_flags["send"], body)

            if len(self.filters) > 0:
                terms = [term for term in self.filters]
                terms.sort(key=len, reverse=True)
                for term in terms:
                    context_filters = self.filters[term]
                    replace = len([ai for ai in context_filters if ai.rule.body_redact]) > 0
                    send = len([ai for ai in context_filters if ai.rule.body_event]) > 0
                    send_event, body = filterx(body, replace, send, term)
                    if send_event:
                        for context_filter in context_filters:
                            if context_filter.type == ContextFilter.DATABASE:
                                dlpe = DlpEvent(self.route_id, self.fullpath, DlpEvent.FOUND_IN_BODY,
                                                context_filter.rule.id).for_database(
                                                    context_filter.database,
                                                    context_filter.schema,
                                                    context_filter.table,
                                                    context_filter.field)
                                TCellAgent.send(dlpe)
                            elif context_filter.type == ContextFilter.REQUEST:
                                dlpe = DlpEvent(self.route_id, self.fullpath, DlpEvent.FOUND_IN_BODY,
                                                context_filter.rule.id).for_request(
                                                    context_filter.context,
                                                    context_filter.parameter)
                                TCellAgent.send(dlpe)
            if self.session_id:
                session_id_actions = dataloss_policy.get_actions_for_session_id()
                if session_id_actions:
                    send_event, body = filterx(body, session_id_actions.body_redact, session_id_actions.body_event,
                                               self.session_id)
                    if send_event:
                        dlpe = DlpEvent(self.route_id, self.fullpath, DlpEvent.FOUND_IN_BODY).for_framework(
                            DlpEvent.FRAMEWORK_VARIABLE_SESSION_ID)
                        TCellAgent.send(dlpe)

        return body

    def filter_log_message(self, msg):
        dataloss_policy = TCellAgent.get_policy(PolicyTypes.DATALOSS)
        if dataloss_policy and dataloss_policy.enabled:
            def filterx(body, replace, send, term):
                send_event_flags = {"send": False}

                def pythong_2_or_3_repl():
                    if not isinstance(body, str):
                        return DataLossPolicy.B_REDACT_MESSAGE
                    return DataLossPolicy.REDACT_MESSAGE

                def repl(found_term):
                    if replace:
                        send_event_flags["send"] = True
                        return pythong_2_or_3_repl()
                    if send:
                        send_event_flags["send"] = True
                    return found_term.group(0)

                if not isinstance(body, str) and isinstance(term, str):
                    encoded_term = term.encode("utf-8")
                else:
                    encoded_term = term
                try:
                    body = re.sub(encoded_term, repl, body)
                except Exception:
                    pass
                return (send_event_flags["send"], body)

            terms = [term for term in self.filters]
            terms.sort(key=len, reverse=True)
            for term in terms:
                context_filters = self.filters[term]
                replace = len([ai for ai in context_filters if ai.rule.log_redact]) > 0
                send = len([ai for ai in context_filters if ai.rule.log_event]) > 0
                send_event, msg = filterx(msg, replace, send, term)
                if send_event:
                    for context_filter in context_filters:
                        if context_filter.type == ContextFilter.DATABASE:
                            dlpe = DlpEvent(self.route_id, self.fullpath, DlpEvent.FOUND_IN_LOG,
                                            context_filter.rule.id).for_database(
                                                context_filter.database,
                                                context_filter.schema,
                                                context_filter.table,
                                                context_filter.field)
                            TCellAgent.send(dlpe)
                        elif context_filter.type == ContextFilter.REQUEST:
                            dlpe = DlpEvent(self.route_id, self.fullpath, DlpEvent.FOUND_IN_LOG,
                                            context_filter.rule.id).for_request(
                                                context_filter.context,
                                                context_filter.parameter)
                            TCellAgent.send(dlpe)
            session_id_actions = dataloss_policy.get_actions_for_session_id()
            if session_id_actions:
                send_event, msg = filterx(msg, session_id_actions.log_redact, session_id_actions.log_event,
                                          self.session_id)
                if send_event:
                    dlpe = DlpEvent(self.route_id, self.fullpath, DlpEvent.FOUND_IN_LOG).for_framework(
                        DlpEvent.FRAMEWORK_VARIABLE_SESSION_ID)
                    TCellAgent.send(dlpe)
        return msg
