# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

from tcell_agent.events.base_event import SensorEvent


class DiscoveryEvent(SensorEvent):
    DATABASE_TYPE = "db"

    def __init__(self,
                 route_id=None):
        super(DiscoveryEvent, self).__init__("discovery")
        if route_id is not None:
            self["rid"] = route_id

    def for_database(self, database, schema, table, field):
        self["type"] = "db"
        self["db"] = database
        self["schema"] = schema
        self["table"] = table
        self["field"] = field
        return self

    def for_database_fields(self, database, schema, table, fields):
        self["type"] = "db"
        self["db"] = database
        self["schema"] = schema
        self["table"] = table
        self["fields"] = fields
        return self
