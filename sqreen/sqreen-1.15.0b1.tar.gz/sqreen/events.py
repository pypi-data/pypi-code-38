# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Sqreen attack event helpers and placeholder
"""
import traceback
from logging import getLogger

from .config import CONFIG
from .remote_exception import traceback_formatter
from .sanitizer import strip_sensitive_data

LOGGER = getLogger(__name__)


def get_context_payload():
    """ Return attack payload dependent on the context, right now stacktrace.
    """
    return {
        "context": {
            "backtrace": list(traceback_formatter(traceback.extract_stack()))
        }
    }


class Attack(object):
    def __init__(self, payload, rule_name):
        self.payload = payload
        self.rule_name = rule_name

    def to_dict(self):
        result = {}
        rule_payload = self.payload.get("rule", {})
        request_payload = self.payload.get("request", {})
        local_payload = self.payload.get("local", {})
        if "name" in rule_payload:
            result["rule_name"] = rule_payload["name"]
        if "rulespack_id" in rule_payload:
            result["rulespack_id"] = rule_payload["rulespack_id"]
        if "test" in rule_payload:
            result["test"] = rule_payload["test"]
        if "infos" in self.payload:
            result["infos"] = self.payload["infos"]
        if "time" in local_payload:
            result["time"] = local_payload["time"]
        if "remote_ip" in request_payload:
            result["client_ip"] = request_payload["remote_ip"]
        if "request" in self.payload:
            result["request"] = self.payload["request"]
        if "params" in self.payload:
            result["params"] = self.payload["params"]
        if "context" in self.payload:
            result["context"] = self.payload["context"]
        if "headers" in self.payload:
            result["headers"] = self.payload["headers"]
        return result


class RequestRecord(object):
    """Request record objects."""

    VERSION = "20171208"

    def __init__(self, payload):
        self.payload = payload

    def to_dict(self):
        """Export the record as a dict object."""
        result = {"version": self.VERSION}
        if "observed" in self.payload:
            observed_dict = self.payload["observed"]
            result["observed"] = observed_dict
            rulespack = None
            for attack_dict in observed_dict.get("attacks", []):
                rulespack = attack_dict.pop("rulespack_id", None) or rulespack
            for exc_dict in observed_dict.get("sqreen_exceptions", []):
                payload_dict = exc_dict.pop("exception", None)
                if payload_dict:
                    exc_dict["message"] = payload_dict["message"]
                    exc_dict["klass"] = payload_dict["klass"]
                rulespack = exc_dict.pop("rulespack_id", None) or rulespack
            if rulespack:
                result["rulespack_id"] = rulespack
            if "observations" in observed_dict:
                result["observed"]["observations"] = [
                    {"category": cat, "key": key, "value": value, "time": time}
                    for (cat, time, key, value) in observed_dict[
                        "observations"
                    ]
                ]
            if "sdk" in observed_dict:
                result["observed"]["sdk"] = [
                    {"name": entry[0], "time": entry[1], "args": entry[2:]}
                    for entry in observed_dict["sdk"]
                ]
        if "local" in self.payload:
            result["local"] = self.payload["local"]
        if "request" in self.payload:
            request_dict = self.payload["request"]
            result["request"] = request_dict
            if "client_ip" in request_dict:
                result["client_ip"] = request_dict.pop("client_ip")
        else:
            result["request"] = {}
        if "params" in self.payload:
            result["request"]["parameters"] = self.payload["params"]
        if "headers" in self.payload:
            result["request"]["headers"] = self.payload["headers"]

        if CONFIG["STRIP_SENSITIVE_DATA"]:
            result["request"] = strip_sensitive_data(result["request"])

        if "response" in self.payload:
            result["response"] = self.payload["response"]

        return result
