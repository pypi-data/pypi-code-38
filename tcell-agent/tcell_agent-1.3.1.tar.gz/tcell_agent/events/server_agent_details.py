# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

from tcell_agent.system_info import current_username, \
     current_group_id, python_version_string
from tcell_agent.events.base_event import SensorEvent


class ServerAgentDetailsEvent(SensorEvent):
    def __init__(self):
        super(ServerAgentDetailsEvent, self).__init__("server_agent_details")
        user = current_username()
        group = current_group_id()
        if user:
            self["user"] = user
        if group:
            self["group"] = group
        self["language"] = "Python"
        self["language_version"] = python_version_string()
