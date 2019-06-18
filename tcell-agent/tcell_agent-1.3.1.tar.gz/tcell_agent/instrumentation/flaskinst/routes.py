from flask import Flask

from tcell_agent.agent import TCellAgent
from tcell_agent.instrumentation.decorators import catches_generic_exception
from tcell_agent.routes.route_info import RouteInfo
from tcell_agent.routes.routes_sender import ensure_routes_sent
from tcell_agent.sanitize.sanitize_utils import python_dependent_hash


ROUTE_TABLE = []
_REPORT_ROUTE = False


def is_report_route():
    return _REPORT_ROUTE


def enable_report_route():
    global _REPORT_ROUTE  # pylint: disable=global-statement
    _REPORT_ROUTE = True


def calculate_route_id(method, uri):
    return str(python_dependent_hash("{method}|{uri}".format(method=method.lower(), uri=uri)))


def get_methods(options, view_func):
    route_methods = options.get("methods", None)
    if route_methods is None:
        route_methods = getattr(view_func, "methods", None) or ("get",)
    return [item.upper() for item in route_methods]


def get_route_target(view_func):
    return ".".join(
        [getattr(view_func, "__module__", ""),
         getattr(view_func, "__name__", "")]
    ).strip(".") or "(dynamic)"


def create_route_info(rule, view_func, method):
    # view_func can be a `functools.partial`. in that case, get
    # the wrapped function and report its information to tcell
    view_func = getattr(view_func, "func", view_func)
    route_url = rule
    route_method = method
    route_target = get_route_target(view_func)
    route_id = calculate_route_id(method, rule)

    return RouteInfo(route_url,
                     route_method,
                     route_target,
                     route_id)


@catches_generic_exception(__name__, "Error discovering route")
def discover_route(rule, view_func, options):
    for method in get_methods(options, view_func):
        route_info = create_route_info(rule, view_func, method)
        if is_report_route():
            TCellAgent.discover_routes([route_info])
        else:
            ROUTE_TABLE.append(route_info)


@catches_generic_exception(__name__, "Error instrumenting routes")
def instrument_routes():
    old_flask_add_url_rule = Flask.add_url_rule

    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        discover_route(rule, view_func, options)
        return old_flask_add_url_rule(self, rule, endpoint, view_func, **options)

    Flask.add_url_rule = add_url_rule


def get_and_reset_route_table():
    global ROUTE_TABLE  # pylint: disable=global-statement
    route_table_copy = list(ROUTE_TABLE)
    ROUTE_TABLE = []
    return route_table_copy


@catches_generic_exception(__name__, "Error reporting routes")
def report_routes():
    # This gets called before first app request.
    # Report all routes collected on app startup.
    # Since routes can still be added dynamically
    # as the app runs, ensure every route added
    # as the app is running is reported right away
    enable_report_route()
    ensure_routes_sent(get_and_reset_route_table)
