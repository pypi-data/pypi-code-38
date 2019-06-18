# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

from tcell_agent.instrumentation.decorators import catches_generic_exception
from tcell_agent.instrumentation.djangoinst.compatability import get_route_handler, \
     get_url_patterns, is_django_20
from tcell_agent.routes.route_info import RouteInfo
from tcell_agent.sanitize.sanitize_utils import python_dependent_hash
from tcell_agent.agent import TCellAgent
from tcell_agent.policies.policy_types import PolicyTypes


ROUTE_TABLE = {}


# Note: for unit tests
def reset_route_table():
    global ROUTE_TABLE  # pylint: disable=global-statement
    ROUTE_TABLE = {}


# Note: for unit tests
def get_route_table():
    return ROUTE_TABLE


def get_resolver_match(request):
    if hasattr(request, "resolver_match") and request.resolver_match:
        return request.resolver_match

    return get_route_handler(request.path_info)


def get_route_id(request):
    system_enablements = TCellAgent.get_policy(PolicyTypes.SYSTEM_ENABLEMENTS)
    if not system_enablements.send_routes_enabled:
        return None
    resolver_match = get_resolver_match(request)
    if resolver_match:
        route_item = ROUTE_TABLE.get(resolver_match.func)
        if route_item:
            return route_item.route_id

    return None


def calculate_route_id(uri):
    return str(python_dependent_hash(uri))


def get_route_target(callback):
    # callback can be a `functools.partial`. in that case, get
    # the wrapped function and report its information to tcell
    callback = getattr(callback, "func", callback)
    if hasattr(callback, "__name__"):
        return callback.__module__ + "." + callback.__name__

    return callback.__module__ + "." + callback.__class__.__name__


def clean_regex_pattern(regex_pattern):
    if regex_pattern.startswith("^"):
        regex_pattern = regex_pattern[1:]
    if regex_pattern.endswith("$"):
        regex_pattern = regex_pattern[:-1]

    return regex_pattern


def get_django20_route_url(prefix, pattern):
    if pattern.__class__.__name__ == "RegexPattern":
        return prefix + clean_regex_pattern(pattern._regex)

    # it's a RoutePattern class
    return prefix + pattern._route


def get_route_url(prefix, entry):
    if is_django_20():
        return get_django20_route_url(prefix, entry.pattern)

    return prefix + clean_regex_pattern(entry.regex.pattern)


# django2+ uses URLResolver and URLPattern,
# RegexURLResolver and RegexURLPattern are used
# by earlier versions.
#
# django 1.5 - 1.9
# django.core.urlresolvers.RegexURLResolver
# django.core.urlresolvers.RegexURLPattern
#
# django 1.10 - 1.11
# django.urls.resolvers.RegexURLResolver
# django.urls.resolvers.RegexURLPattern
#
# django 2.0
# django.urls.resolvers.URLResolver
# django.urls.resolvers.URLPattern
@catches_generic_exception(__name__, "Error parsing route")
def process_url_entry(entry, prefix):
    route_url = get_route_url(prefix, entry)
    route_callback = entry.callback

    entry_class_name = entry.__class__.__name__
    if entry_class_name in ["RegexURLResolver", "URLResolver"]:
        populate_route_table(entry.url_patterns, route_url)
    elif route_callback and (entry_class_name in ["RegexURLPattern", "URLPattern"]):
        route_target = get_route_target(route_callback)
        route_id = calculate_route_id(route_url)
        ROUTE_TABLE[route_callback] = RouteInfo(route_url,
                                                "*",
                                                route_target,
                                                route_id)


def populate_route_table(urllist, prefix=""):
    for entry in urllist:
        process_url_entry(entry, prefix)

    return ROUTE_TABLE


def make_route_table():
    return populate_route_table(get_url_patterns()).values()
