# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

# Agent Module handles communication and instrumentation, this
# is the main class.

from __future__ import unicode_literals
from collections import defaultdict

from tcell_agent.events.app_route import AppRouteSensorEvent
from tcell_agent.events.discovery import DiscoveryEvent
from tcell_agent.tcell_logger import get_module_logger


def inner_dict(n):
    return lambda: defaultdict(n)


def hash_database_tuple(database, schema, table, fields):
    return hash(database + "," + schema + "," + table + "," + ",".join(fields))


class DataExfilRule(object):
    def __init__(self):
        self.body_event = False
        self.body_redact = False
        self.body_hash = False
        self.log_event = False
        self.log_redact = False
        self.log_hash = False
        self.id = 0


class DatabaseFieldEndpoint(dict):
    def __init__(self):
        dict.__init__(self)
        self.discovered = False
        self.data_exfil_rule = None


class RouteEndpoint(object):
    def __init__(self):
        self.discovered = False
        self.database_fields = inner_dict(DatabaseFieldEndpoint)()
        self.database_exfil_rules = inner_dict(inner_dict(inner_dict(inner_dict(DatabaseFieldEndpoint))))()

    def has_field_been_discovered(self, database, schema, table, field):
        return self.have_fields_been_discovered(database, schema, table, [field])

    def have_fields_been_discovered(self, database, schema, table, fields):
        if database and schema and table and fields:
            if not self.database_fields[hash_database_tuple(database, schema, table, fields)].discovered:
                return True
        return False

    def set_field_discovered(self, database, schema, table, field):
        self.set_fields_discovered(database, schema, table, [field])

    def set_fields_discovered(self, database, schema, table, fields):
        if database and schema and table and fields:
            self.database_fields[hash_database_tuple(database, schema, table, fields)].discovered = True


class RouteTable(object):
    def __init__(self):
        get_module_logger(__name__).info("Initializing route table.")
        self.routes = defaultdict(RouteEndpoint)
        self.discovered_routed_ids = set()

    def discover_routes(self, routes_info, send_events_func):
        route_events_to_send = []
        for route_info in routes_info:
            if route_info.route_id not in self.discovered_routed_ids:
                route_events_to_send.append(
                    AppRouteSensorEvent(
                        route_info.route_url,
                        route_info.route_method,
                        route_info.route_target,
                        route_info.route_id
                    )
                )
                self.discovered_routed_ids.add(route_info.route_id)

        send_events_func(route_events_to_send)

    def discover_database_fields(self,
                                 database,
                                 schema,
                                 table,
                                 fields,
                                 route_id,
                                 send_event_func):
        if route_id is None:
            route_id = ""

        if self.routes[route_id].have_fields_been_discovered(database,
                                                             schema,
                                                             table,
                                                             fields):
            self.routes[route_id].set_fields_discovered(database,
                                                        schema,
                                                        table,
                                                        fields)
            event = DiscoveryEvent(route_id).for_database_fields(database,
                                                                 schema,
                                                                 table,
                                                                 fields)
            send_event_func(event)
