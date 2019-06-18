# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

from tcell_agent.events.base_event import SensorEvent
from tcell_agent.utils.strings import ensure_string


class AppConfigSettings(SensorEvent):
    def __init__(self, package, section, name, value, prefix=None):
        super(AppConfigSettings, self).__init__("app_config_setting", ensure_delivery=True, queue_wait=True)
        self.setting(package, section, prefix, name, value)

    def setting(self, package, section, prefix, name, value):
        self["package"] = package
        self["section"] = section
        if prefix is not None:
            self["prefix"] = prefix
        self["name"] = name
        if value is None:
            self["value"] = ""
        else:
            self["value"] = ensure_string(value).lower()
