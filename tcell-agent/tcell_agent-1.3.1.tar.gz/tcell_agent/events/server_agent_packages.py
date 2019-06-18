# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

from tcell_agent.events.base_event import SensorEvent


class ServerAgentPackagesEvent(SensorEvent):
    def __init__(self):
        super(ServerAgentPackagesEvent, self).__init__(
            "server_agent_packages",
            ensure_delivery=True,
            flush_right_away=True)
        self.flush = True
        self.ensure = True
        self["packages"] = []

    def add_package(self, name, version, lic=None):
        package = {"n": name, "v": version}
        if lic is not None:
            package["l"] = lic
        self["packages"].append(package)
