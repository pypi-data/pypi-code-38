# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

from tcell_agent.events.base_event import SensorEvent


class AppRouteSensorEvent(SensorEvent):
    def __init__(self, uri, method, destination, rid, params=None):
        super(AppRouteSensorEvent, self).__init__("appserver_routes", ensure_delivery=True, queue_wait=True)
        self["uri"] = uri
        self["destination"] = destination
        self["method"] = method
        self["rid"] = rid
        if params is not None:
            self["params"] = params
