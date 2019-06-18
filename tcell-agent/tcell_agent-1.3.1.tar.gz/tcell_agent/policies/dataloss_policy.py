# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

from tcell_agent.policies.base_policy import TCellPolicy
from collections import defaultdict
import collections

# "dlp": {
#   "v":1,
#   "policy_id":"xyz-def",
#   "data":{
#     "protections":[
#       {"table":"work_infos",
#        "field":"SSN",
#        "actions":{"body":["redact"], "log":["redact"]}
#       },
#       {"table":"work_infos",
#        "field":"income",
#        "actions":{"body":["redact"], "log":["redact"]}
#       }
#     ]
#   }
# },
# "request_protections": [
#   {
#     "id": "129321",
#     "scope": "route",
#     "route_ids": ["234234", "34432432"],
#     "variable_context": "form",
#     "variables": ["password"],
#     "actions": {
#       "body": ["event"],
#       "log": ["redact"]
#     }
#   },
# ]


class DataLossPolicyEnforcement(object):
    def __init__(self):
        self.body_event = False
        self.body_redact = False
        self.body_hash = False
        self.log_event = False
        self.log_redact = False
        self.log_hash = False
        self.value_regex = None
        self.id = 0

    def apply_regex(self, value):  # pylint: disable=no-self-use
        # TODO: apply the regex to the value pylint: disable=fixme
        return value


class RequestProtectionManager(object):
    FORM = "form"
    COOKIE = "cookie"
    HEADER = "header"

    def __init__(self):
        def inner_dict(n):
            return lambda: collections.defaultdict(n)

        # ["route_id"]["parameter"] = set(Rule1, Rule2)
        self.parameter_protections = inner_dict(inner_dict(set))()
        self.cookie_protections = inner_dict(inner_dict(set))()
        self.header_protections = inner_dict(inner_dict(set))()

    def add_form_protection(self, form_parameter, rule, route_id="*"):
        if form_parameter is not None:
            self.parameter_protections[form_parameter.lower()][route_id].add(rule)

    def get_rules_for_form_parameter(self, form_parameter, route_id="*"):
        return_actions = set()
        if form_parameter in self.parameter_protections:
            if route_id in self.parameter_protections[form_parameter]:
                return_actions = return_actions.union(self.parameter_protections[form_parameter][route_id])
            elif route_id != "*" and "*" in self.parameter_protections[form_parameter]:
                return_actions = return_actions.union(self.parameter_protections[form_parameter]["*"])
        if len(return_actions) == 0:
            return None
        return return_actions

    def add_cookie_protection(self, cookie_name, rule, route_id="*"):
        if cookie_name:
            self.cookie_protections[cookie_name][route_id].add(rule)

    def get_rules_for_cookie(self, cookie_name, route_id="*"):
        return_actions = set()
        if cookie_name in self.cookie_protections:
            if route_id in self.cookie_protections[cookie_name]:
                return_actions = return_actions.union(self.cookie_protections[cookie_name][route_id])
            elif route_id != "*" and "*" in self.cookie_protections[cookie_name]:
                return_actions = return_actions.union(self.cookie_protections[cookie_name]["*"])
        if len(return_actions) == 0:
            return None
        return return_actions

    def add_header_protection(self, header_name, rule, route_id="*"):
        if header_name:
            self.header_protections[header_name][route_id].add(rule)

    def get_rules_for_header(self, header_name, route_id="*"):
        return_actions = set()
        if header_name in self.header_protections:
            if route_id in self.header_protections[header_name]:
                return_actions = return_actions.union(self.header_protections[header_name][route_id])
            elif route_id != "*" and "*" in self.header_protections[header_name]:
                return_actions = return_actions.union(self.header_protections[header_name]["*"])
        if len(return_actions) == 0:
            return None
        return return_actions


class DataLossPolicy(TCellPolicy):
    REDACT_MESSAGE = "[redact]"
    B_REDACT_MESSAGE = b"[redact]"
    api_identifier = "dlp"

    def __init__(self, _, __, policy_json):
        super(DataLossPolicy, self).__init__()
        self.init_fields()
        if policy_json is not None:
            self.load_from_json(policy_json)

    def init_fields(self):
        self.enabled = False
        self.database_discovery_enabled = False

        self.field_redact_body = set()
        self.field_alerts = set()

        self.session_id_actions = []
        self.table_field_actions = defaultdict(list)

        def inner_dict(n):
            return lambda: collections.defaultdict(n)

        # [db][schema][table][field] = actions
        self.database_protections = inner_dict(inner_dict(inner_dict(inner_dict(inner_dict(set)))))()
        self.request_protections = RequestProtectionManager()
        self.session_id_filter_actions = None

    def get_actions_for_session_id(self):
        return self.session_id_filter_actions

    def get_actions_for_db_field(self, database, schema, table, field, route="*"):
        return_actions = set()
        for d in (database, "*"):
            if d not in self.database_protections:
                continue
            for s in (schema, "*"):
                if s not in self.database_protections[d]:
                    continue
                for t in (table, "*"):
                    if t not in self.database_protections[d][s]:
                        continue
                    for f in (field, "*"):
                        if f in self.database_protections[d][s][t]:
                            if route in self.database_protections[d][s][t][f]:
                                return_actions = return_actions.union(self.database_protections[d][s][t][f][route])
                            elif route != "*" and "*" in self.database_protections[d][s][t][f]:
                                return_actions = return_actions.union(self.database_protections[d][s][t][f]["*"])
        if len(return_actions) == 0:
            return None
        return return_actions

    def get_actions_for_form_parameter(self, parameter, route_id="*"):
        return self.request_protections.get_rules_for_form_parameter(parameter, route_id)

    def get_actions_for_cookie(self, cookie_name, route_id="*"):
        return self.request_protections.get_rules_for_cookie(cookie_name, route_id)

    def get_actions_for_header(self, header_name, route_id="*"):
        return self.request_protections.get_rules_for_header(header_name, route_id)

    def load_from_json(self, policy_json):
        self.init_fields()
        if "policy_id" in policy_json:
            self.policy_id = policy_json["policy_id"]
        else:
            raise Exception("Policy Id Not Found")

        policy_data_json = policy_json.get("data")

        def actions_from_json(protections):
            actions = None
            body = protections.get("body", [])
            if "redact" in body:
                actions = actions or DataLossPolicyEnforcement()
                actions.body_redact = True
            if "event" in body:
                actions = actions or DataLossPolicyEnforcement()
                actions.body_event = True
            if "hash" in body:
                actions = actions or DataLossPolicyEnforcement()
                actions.body_hash = True
            log = protections.get("log", [])
            if "redact" in log:
                actions = actions or DataLossPolicyEnforcement()
                actions.log_redact = True
            if "event" in log:
                actions = actions or DataLossPolicyEnforcement()
                actions.log_event = True
            if "hash" in log:
                actions = actions or DataLossPolicyEnforcement()
                actions.log_hash = True
            return actions

        if policy_data_json:
            data_discovery_json = policy_data_json.get("data_discovery")
            if data_discovery_json is not None:
                self.database_discovery_enabled = data_discovery_json.get("database_enabled", False)
                self.enabled = self.database_discovery_enabled

            session_id_protection = policy_data_json.get("session_id_protections", [])
            if session_id_protection:
                self.session_id_filter_actions = actions_from_json(session_id_protection)
                self.enabled = self.enabled or self.session_id_filter_actions is not None
            request_protections = policy_data_json.get("request_protections", [])
            self.enabled = self.enabled or len(request_protections) > 0
            for protection in request_protections:
                # "id": "129321",
                # "scope": "route",
                # "route_ids": ["234234", "34432432"],
                # "variable_context": "form",
                # "variables": ["password"],
                scope = protection.get("scope")
                variable_context = protection.get("variable_context", None)
                variables = protection.get("variables", None)
                actions = protection.get("actions", {})
                rule_id = protection.get("id", 0)
                if variable_context is None or variables is None:
                    continue
                route_ids = []
                if scope is None or scope == "global":
                    route_ids = ["*"]
                elif scope == "route":
                    route_ids = protection.get("route_ids", [])
                rule = actions_from_json(actions)
                if rule is None:
                    continue
                rule.id = rule_id
                for route_id in route_ids:
                    for variable in variables:
                        if variable_context == RequestProtectionManager.FORM or variable_context == "parameter":
                            self.request_protections.add_form_protection(variable.lower(), rule, route_id)
                        elif variable_context == RequestProtectionManager.COOKIE:
                            # cookie names are case sensitive
                            self.request_protections.add_cookie_protection(variable, rule, route_id)
                        elif variable_context == RequestProtectionManager.HEADER:
                            self.request_protections.add_header_protection(variable.lower(), rule, route_id)

            protections = policy_data_json.get("db_protections", [])
            self.enabled = self.enabled or len(protections) > 0
            for protection in protections:
                databases = protection.get("databases", ["*"])
                scope = protection.get("scope")
                schemas = protection.get("schemas", ["*"])
                tables = protection.get("tables", ["*"])
                fields = protection.get("fields", None)
                actions = protection.get("actions", {})
                rule_id = protection.get("id", 0)

                if fields is None:
                    continue
                route_ids = []
                if scope is None or scope == "global":
                    route_ids = ["*"]
                if scope == "route":
                    route_ids = protection.get("route_ids", [])
                field_actions = actions_from_json(actions)
                if field_actions is None:
                    continue
                field_actions.id = rule_id
                if databases and schemas and tables and fields:
                    if "*" in databases:
                        databases = ["*"]
                    for database in databases:
                        if "*" in schemas:
                            schemas = ["*"]
                        for schema in schemas:
                            if "*" in tables:
                                tables = ["*"]
                            for table in tables:
                                if "*" in fields:
                                    fields = ["*"]
                                for field in fields:
                                    if "*" in route_ids:
                                        route_ids = ["*"]
                                    for route_id in route_ids:
                                        self.database_protections[database][schema][table][field][route_id].add(
                                            field_actions)
