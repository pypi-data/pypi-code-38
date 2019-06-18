from __future__ import print_function

import unittest

from mock import Mock, call, patch, PropertyMock

from tcell_agent.agent import TCellAgent
from tcell_agent.routes.routes_sender import create_and_send_routes, \
     ensure_routes_sent, send_routes, _ROUTES_SEND_LOCK


def routes_getter_func():
    return []


class EnsureRoutesSentTest(unittest.TestCase):
    def test_routes_already_sent_ensure_routes_sent(self):
        get_mock = Mock()
        agent_mock = Mock(policies_manager=PropertyMock(get=get_mock))

        with patch.object(TCellAgent, "get_agent", return_value=agent_mock):
            with patch("tcell_agent.routes.routes_sender.has_route_table_been_sent",
                       return_value=True) as patched_has_route_table_been_sent:
                with patch("tcell_agent.routes.routes_sender.create_and_send_routes") as patched_create_and_send_routes:
                    with patch("tcell_agent.routes.routes_sender.set_route_table_has_been_sent") as patched_set_route_table_has_been_sent:
                        ensure_routes_sent(routes_getter_func)

                        self.assertTrue(patched_has_route_table_been_sent.called)
                        self.assertFalse(patched_create_and_send_routes.called)
                        self.assertFalse(patched_set_route_table_has_been_sent.called)

                        try:
                            self.assertTrue(
                                _ROUTES_SEND_LOCK.acquire(False),
                                "Lock should be open")
                        finally:
                            _ROUTES_SEND_LOCK.release()

    def test_routes_need_sending_ensure_routes_sent(self):
        get_mock = Mock()
        agent_mock = Mock(policies_manager=PropertyMock(get=get_mock))

        with patch.object(TCellAgent, "get_agent", return_value=agent_mock):
            with patch("tcell_agent.routes.routes_sender.has_route_table_been_sent",
                       return_value=False) as patched_has_route_table_been_sent:
                with patch("tcell_agent.routes.routes_sender.create_and_send_routes") as patched_create_and_send_routes:
                    with patch("tcell_agent.routes.routes_sender.set_route_table_has_been_sent") as patched_set_route_table_has_been_sent:
                        ensure_routes_sent(routes_getter_func)

                        self.assertTrue(patched_has_route_table_been_sent.called)
                        self.assertTrue(patched_create_and_send_routes.called)
                        self.assertTrue(patched_set_route_table_has_been_sent.called)

                        try:
                            self.assertTrue(
                                _ROUTES_SEND_LOCK.acquire(False),
                                "Lock should be open")
                        finally:
                            _ROUTES_SEND_LOCK.release()

    def test_other_thread_sent_routes_ensure_routes_sent(self):
        get_mock = Mock()
        agent_mock = Mock(policies_manager=PropertyMock(get=get_mock))

        with patch.object(TCellAgent, "get_agent", return_value=agent_mock):
            with patch("tcell_agent.routes.routes_sender.has_route_table_been_sent",
                       side_effect=[False, True]) as patched_has_route_table_been_sent:
                with patch("tcell_agent.routes.routes_sender.create_and_send_routes") as patched_create_and_send_routes:
                    with patch("tcell_agent.routes.routes_sender.set_route_table_has_been_sent") as patched_set_route_table_has_been_sent:
                        ensure_routes_sent(routes_getter_func)

                        self.assertEqual(patched_has_route_table_been_sent.call_count, 2)
                        self.assertFalse(patched_create_and_send_routes.called)
                        self.assertFalse(patched_set_route_table_has_been_sent.called)

                        try:
                            self.assertTrue(
                                _ROUTES_SEND_LOCK.acquire(False),
                                "Lock should be open")
                        finally:
                            _ROUTES_SEND_LOCK.release()


class SendRoutesTest(unittest.TestCase):
    def test_send_routes(self):
        routes = ["not a real object one"]
        with patch.object(TCellAgent, "discover_routes") as patched_discover_routes:
            send_routes(routes)
            self.assertTrue(patched_discover_routes.called)
            self.assertEqual(patched_discover_routes.call_args_list,
                             [call(("not a real object one",))])

    def test_exception_handling_in_send_routes(self):
        logger_mock = Mock(error=Mock(), exception=Mock())
        routes = ["not a real object one"]
        with patch.object(TCellAgent,
                          "discover_routes",
                          side_effect=Exception("test exception handling")):
            with patch("tcell_agent.instrumentation.decorators.get_module_logger",
                       return_value=logger_mock) as patched_get_module_logger:
                send_routes(routes)

                self.assertTrue(logger_mock.error.called)
                self.assertTrue(logger_mock.exception.called)
                self.assertEqual(logger_mock.error.call_args_list,
                                 [call("Exception reporting routes: test exception handling")])
                self.assertEqual(patched_get_module_logger.call_args_list,
                                 [call("tcell_agent.routes.routes_sender")])


class CreateAndSendRoutesTest(unittest.TestCase):
    def test_exception_handling_in_create_and_send_routes(self):
        func = Mock(side_effect=Exception("test exception handling"))
        logger_mock = Mock(error=Mock(), exception=Mock())
        with patch("tcell_agent.instrumentation.decorators.get_module_logger",
                   return_value=logger_mock) as patched_get_module_logger:
            create_and_send_routes(func)

            self.assertTrue(logger_mock.error.called)
            self.assertTrue(logger_mock.exception.called)
            self.assertEqual(logger_mock.error.call_args_list,
                             [call("Error creating routes to report: test exception handling")])
            self.assertEqual(patched_get_module_logger.call_args_list,
                             [call("tcell_agent.routes.routes_sender")])
