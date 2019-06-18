import unittest

from mock import Mock, call, patch

from functools import partial

from tcell_agent.utils.compat import PY2
from tcell_agent.instrumentation.djangoinst.routes import \
     get_route_target, calculate_route_id, clean_regex_pattern, \
     get_route_url, populate_route_table, reset_route_table, \
     get_route_table


# callback can be a class object when using:
# django.contrib.syndication.views.Feed. Examples
# here: https://docs.djangoproject.com/en/2.1/ref/contrib/syndication/
class RssLatestPackagesFeed(object):
    pass


def view_func(_):
    pass


partial_wrapped_viev_func = partial(view_func, "default")


class GetRouteTargetTest(unittest.TestCase):
    def test_class_get_route_target(self):
        route_target = get_route_target(RssLatestPackagesFeed())
        self.assertEqual(
            route_target,
            "tcell_agent.tests.instrumentation.djangoinst.routes_test.RssLatestPackagesFeed"
        )

    def test_func_get_route_target(self):
        route_target = get_route_target(view_func)
        self.assertEqual(
            route_target,
            "tcell_agent.tests.instrumentation.djangoinst.routes_test.view_func"
        )

    def test_partial_wrapped_func_get_route_target(self):
        route_target = get_route_target(partial_wrapped_viev_func)
        self.assertEqual(
            route_target,
            "tcell_agent.tests.instrumentation.djangoinst.routes_test.view_func"
        )


class CalculateRouteIdTest(unittest.TestCase):
    def test_calculate_route_id(self):
        if PY2:
            self.assertEqual(calculate_route_id("/uri"), "-7649691677039210269")
        else:
            self.assertEqual(calculate_route_id("/uri"), "1516253")


class CleanRegexPatternTest(unittest.TestCase):
    def test_clean_regex_pattern(self):
        self.assertEqual(
            clean_regex_pattern("^response-size/(d+)$"),
            "response-size/(d+)"
        )


class GetRouteUrlTest(unittest.TestCase):
    class RegexPattern(object):
        def __init__(self, regex):
            self._regex = regex

    class RoutePattern(object):
        def __init__(self, route):
            self._route = route

    def test_django1_get_route_url(self):
        regex = Mock(pattern="some/path")
        entry = Mock(regex=regex)
        with patch("tcell_agent.instrumentation.djangoinst.routes.is_django_20",
                   return_value=False) as patched_is_django_20:
            route_url = get_route_url("prefix/", entry)
            self.assertTrue(patched_is_django_20.called)
            self.assertEqual(route_url, "prefix/some/path")

    def test_django2_get_route_url(self):
        pattern = self.RegexPattern("^response-size/(d+)$")
        entry = Mock(pattern=pattern)
        with patch("tcell_agent.instrumentation.djangoinst.routes.is_django_20",
                   return_value=True) as patched_is_django_20:
            route_url = get_route_url("prefix/", entry)
            self.assertTrue(patched_is_django_20.called)
            self.assertEqual(route_url, "prefix/response-size/(d+)")

        pattern = self.RoutePattern("blog")
        entry = Mock(pattern=pattern)
        with patch("tcell_agent.instrumentation.djangoinst.routes.is_django_20",
                   return_value=True) as patched_is_django_20:
            route_url = get_route_url("prefix/", entry)
            self.assertTrue(patched_is_django_20.called)
            self.assertEqual(route_url, "prefix/blog")


class PopulateRouteTableTest(unittest.TestCase):
    class RegexURLPattern(object):
        def __init__(self, callback):
            self.callback = callback

    class URLPattern(object):
        def __init__(self, callback):
            self.callback = callback

    class RegexURLResolver(object):
        def __init__(self, url_patterns, callback):
            self.url_patterns = url_patterns
            self.callback = callback

    class URLResolver(object):
        def __init__(self, url_patterns, callback):
            self.url_patterns = url_patterns
            self.callback = callback

    def internal_populate_route_table(self, urllist):
        reset_route_table()

        with patch("tcell_agent.instrumentation.djangoinst.routes.get_route_url",
                   return_value="/some/url") as patched_get_route_url:
            with patch("tcell_agent.instrumentation.djangoinst.routes.get_route_target",
                       return_value="module.view_func") as patched_get_route_target:
                with patch("tcell_agent.instrumentation.djangoinst.routes.calculate_route_id",
                           return_value="fake-route-id") as patched_calculate_route_id:
                    populate_route_table(urllist)

                    self.assertTrue(patched_get_route_url.called)
                    self.assertTrue(patched_get_route_target.called)
                    self.assertTrue(patched_calculate_route_id.called)

                    route_table = get_route_table()
                    self.assertEqual(len(route_table), 1)
                    route_info = route_table["callback"]
                    self.assertEqual(route_info.route_url, "/some/url")
                    self.assertEqual(route_info.route_method, "*")
                    self.assertEqual(route_info.route_target, "module.view_func")
                    self.assertEqual(route_info.route_id, "fake-route-id")

    def test_populate_route_table(self):
        self.internal_populate_route_table([self.RegexURLPattern("callback")])
        self.internal_populate_route_table([self.URLPattern("callback")])
        self.internal_populate_route_table([self.RegexURLResolver([self.RegexURLPattern("callback")],
                                                                  "callback")])
        self.internal_populate_route_table([self.RegexURLResolver([self.URLPattern("callback")],
                                                                  "callback")])

    def test_invalid_populate_route_table(self):
        logger = Mock(error=Mock(), exception=Mock())
        with patch("tcell_agent.instrumentation.decorators.get_module_logger",
                   return_value=logger) as patched_get_module_logger:
            with patch("tcell_agent.instrumentation.djangoinst.routes.get_route_url",
                       side_effect=Exception("test exception handling")):
                populate_route_table([None])

                route_table = get_route_table()
                self.assertEqual(len(route_table), 0)

                self.assertTrue(patched_get_module_logger.called)
                self.assertTrue(logger.error.called)
                self.assertTrue(logger.exception.called)
                self.assertTrue(patched_get_module_logger.call_args_list, [])
                self.assertEqual(logger.error.call_args_list,
                                 [call("Error parsing route: test exception handling")])
