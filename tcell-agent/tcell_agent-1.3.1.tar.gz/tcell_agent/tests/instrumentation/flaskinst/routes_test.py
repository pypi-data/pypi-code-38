import unittest

from functools import partial
from mock import Mock, patch

from tcell_agent.agent import TCellAgent
from tcell_agent.instrumentation.flaskinst.routes import \
     calculate_route_id, discover_route, get_methods, enable_report_route
from tcell_agent.sanitize.sanitize_utils import USE_PYTHON_2_HASH


enable_report_route()


def index():
    return "/"


class RoutesTest(unittest.TestCase):
    @classmethod
    def api(cls):
        return "/api"

    def test_upper_case_method_calculate_route_id(self):
        if USE_PYTHON_2_HASH:
            self.assertEqual("-8927252616038890182", calculate_route_id("GET", "/"))
        else:
            self.assertEqual("98246921", calculate_route_id("GET", "/"))

    def test_lower_case_method_calculate_route_id(self):
        if USE_PYTHON_2_HASH:
            self.assertEqual("-8927252616038890182", calculate_route_id("get", "/"))
        else:
            self.assertEqual("98246921", calculate_route_id("get", "/"))

    def test_methods_provided_get_methods(self):
        options = {"methods": ["GET", "POST"]}
        methods = get_methods(options, None)
        self.assertEqual(["GET", "POST"], methods)

    def test_view_func_methods_get_methods(self):
        options = {}
        view_func = Mock(methods=["PUT", "DELETE"])
        methods = get_methods(options, view_func)
        self.assertEqual(["PUT", "DELETE"], methods)

    def test_no_methods_get_methods(self):
        options = {}
        view_func = Mock(methods=None)
        methods = get_methods(options, view_func)
        self.assertEqual(["GET"], methods)

    def test_dynamic_discover_route(self):
        options = {"methods": ["GET"]}
        with patch.object(TCellAgent, "discover_routes", return_value=None) as patched_discover_routes:
            discover_route("/", partial(index), options)

            self.assertTrue(patched_discover_routes.called)
            args, _ = patched_discover_routes.call_args
            self.assertEqual(len(args), 1)
            routes = args[0]
            self.assertEqual(len(routes), 1)
            route_info = routes[0]
            self.assertEqual(route_info.route_url, "/")
            self.assertEqual(route_info.route_method, "GET")
            self.assertEqual(
                route_info.route_target,
                "tcell_agent.tests.instrumentation.flaskinst.routes_test.index"
            )
            self.assertEqual(route_info.route_id, calculate_route_id("GET", "/"))

    def test_function_discover_route(self):
        options = {"methods": ["GET"]}
        with patch.object(TCellAgent, "discover_routes", return_value=None) as patched_discover_routes:
            discover_route("/", index, options)

            self.assertTrue(patched_discover_routes.called)
            args, _ = patched_discover_routes.call_args
            self.assertEqual(len(args), 1)
            routes = args[0]
            self.assertEqual(len(routes), 1)
            route_info = routes[0]
            self.assertEqual(route_info.route_url, "/")
            self.assertEqual(route_info.route_method, "GET")
            self.assertEqual(
                route_info.route_target,
                "tcell_agent.tests.instrumentation.flaskinst.routes_test.index"
            )
            self.assertEqual(route_info.route_id, calculate_route_id("GET", "/"))

    def test_bound_method_discover_route(self):
        options = {"methods": ["GET"]}
        with patch.object(TCellAgent, "discover_routes", return_value=None) as patched_discover_routes:
            discover_route("/", RoutesTest.api, options)

            self.assertTrue(patched_discover_routes.called)
            args, _ = patched_discover_routes.call_args
            self.assertEqual(len(args), 1)
            routes = args[0]
            self.assertEqual(len(routes), 1)
            route_info = routes[0]
            self.assertEqual(route_info.route_url, "/")
            self.assertEqual(route_info.route_method, "GET")
            self.assertEqual(
                route_info.route_target,
                "tcell_agent.tests.instrumentation.flaskinst.routes_test.api"
            )
            self.assertEqual(route_info.route_id, calculate_route_id("GET", "/"))
