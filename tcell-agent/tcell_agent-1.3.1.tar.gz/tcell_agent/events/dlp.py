# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

from tcell_agent.sanitize.sanitize_utils import hmac_half, strip_uri
from tcell_agent.events.base_event import SensorEvent
from tcell_agent.utils.strings import ensure_string


class DlpEvent(SensorEvent):
    FOUND_IN_BODY = "body"
    FOUND_IN_LOG = "log"
    FOUND_IN_CONSOLE = "console"

    FRAMEWORK_VARIABLE_SESSION_ID = "session_id"

    REQUEST_CONTEXT_FORM = "form"
    REQUEST_CONTEXT_COOKIE = "cookie"
    REQUEST_CONTEXT_HEADER = "header"

    def __init__(self,
                 route_id,
                 raw_uri,
                 found_in,
                 action_id=None,
                 user_id=None,
                 session_id=None):
        super(DlpEvent, self).__init__("dlp")
        if route_id:
            self["rid"] = route_id
        if raw_uri:
            self["uri"] = strip_uri(raw_uri)
        self["found_in"] = found_in
        if action_id:
            self["rule"] = action_id
        if session_id:
            self["sid"] = hmac_half(session_id)
        if user_id is not None:
            self["uid"] = ensure_string(user_id)

    def for_database(self, database, schema, table, field):
        self["type"] = "db"
        self["db"] = database
        self["schema"] = schema
        self["table"] = table
        self["field"] = field
        return self

    def for_framework(self, framwork_variable):
        self["type"] = "framework"
        self["variable"] = framwork_variable
        return self

    def for_request(self, context, variable):
        self["type"] = "request"
        self["context"] = context
        self["variable"] = variable
        return self
