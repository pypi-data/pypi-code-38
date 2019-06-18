import unittest
import os

from mock import Mock, PropertyMock, call, patch

from tcell_agent.agent import TCellAgent
from tcell_agent.loggers.module_logger import ModuleLogger
from tcell_agent.routes.route_info import RouteInfo
from tcell_agent.rust.native_agent import PlaceholderNativeAgent
from tcell_agent.tests.support.builders import ConfigurationBuilder
from tcell_agent.tests.support.context_library import ConfigContext


class AgentTest(unittest.TestCase):
    def test_existing_agent_init_agent(self):
        TCellAgent.tCell_agent = "already set"

        with patch("tcell_agent.agent.set_native_agent") as patched_set_native_agent:
            TCellAgent.init_agent()

            self.assertFalse(patched_set_native_agent.called)
            self.assertEqual(TCellAgent.tCell_agent, "already set")

    def test_exception_in_init_agent(self):
        config = ConfigurationBuilder().build()
        with patch("tcell_agent.agent.load_native_lib",
                   side_effect=Exception("test exception handling")):
            with patch.object(ModuleLogger, "error") as patched_error:
                with patch.object(ModuleLogger, "exception") as patched_exception:
                    with self.assertRaises(Exception):
                        with ConfigContext(config):
                            TCellAgent.init_agent()

                    self.assertTrue(patched_error.called)
                    self.assertTrue(patched_exception.called)
                    self.assertEqual(patched_error.call_args_list,
                                     [call("Exception creating agent test exception handling")])

    def test_no_agent_init_agent(self):
        TCellAgent.tCell_agent = None

        config = ConfigurationBuilder().build()

        policies_manager_logger = Mock(info=Mock())
        route_discovery_logger = Mock(info=Mock())
        with patch("tcell_agent.agent.set_native_agent") as patched_set_native_agent:
            with patch("tcell_agent.policies.policies_manager.get_module_logger",
                       return_value=policies_manager_logger):
                with patch("tcell_agent.routes.route_discovery.get_module_logger",
                           return_value=route_discovery_logger):
                    with ConfigContext(config):
                        TCellAgent.init_agent()

                    agent = TCellAgent.tCell_agent

                    self.assertTrue(patched_set_native_agent.called)
                    self.assertEqual(type(agent.native_agent), PlaceholderNativeAgent)
                    self.assertEqual(agent.parent_pid, os.getpid())
                    self.assertIsNotNone(agent.policies_manager)
                    self.assertIsNotNone(agent.policy_polling)
                    self.assertIsNotNone(agent.route_table)
                    self.assertEqual(policies_manager_logger.info.call_args_list,
                                     [call("Initializing Policies")])
                    self.assertEqual(route_discovery_logger.info.call_args_list,
                                     [call("Initializing route table.")])

    def test_startup(self):
        agent_mock = Mock(create_native_agent=Mock(),
                          ensure_polling_thread_running=Mock(),
                          send_startup_events=Mock())
        agent_logger_mock = Mock(info=Mock())

        with patch.object(TCellAgent, "get_agent", return_value=agent_mock):
            with patch("tcell_agent.agent.get_module_logger",
                       return_value=agent_logger_mock):
                TCellAgent.startup()
                self.assertTrue(agent_mock.create_native_agent.called)
                self.assertTrue(agent_mock.ensure_polling_thread_running.called)
                self.assertTrue(agent_mock.send_startup_events.called)
                self.assertEqual(agent_logger_mock.info.call_args_list,
                                 [call("Started agent")])

    def test_send(self):
        agent_mock = Mock(send_event=Mock())

        with patch.object(TCellAgent, "get_agent", return_value=agent_mock):
            TCellAgent.send({"event_type": "test"})
            self.assertTrue(agent_mock.send_event.called)
            self.assertEqual(agent_mock.send_event.call_args_list,
                             [call({"event_type": "test"})])

        agent_logger_mock = Mock(error=Mock(), exception=Mock())
        with patch.object(TCellAgent, "get_agent",
                          side_effect=Exception("test exception handling")):
            with patch("tcell_agent.instrumentation.decorators.get_module_logger",
                       return_value=agent_logger_mock):
                TCellAgent.send({"event_type": "test"})
                self.assertTrue(agent_logger_mock.error.called)
                self.assertTrue(agent_logger_mock.exception.called)
                self.assertEqual(agent_logger_mock.error.call_args_list,
                                 [call("Error sending event: test exception handling")])

    def test_get_policy(self):
        get_mock = Mock()
        agent_mock = Mock(policies_manager=PropertyMock(get=get_mock))

        with patch.object(TCellAgent, "get_agent", return_value=agent_mock):
            TCellAgent.get_policy("TestPolicy")
            self.assertTrue(get_mock.called)
            self.assertEqual(get_mock.call_args_list,
                             [call("TestPolicy")])

    def test_request_metric(self):
        report_metrics_mock = Mock()
        agent_mock = Mock(native_agent=PropertyMock(report_metrics=report_metrics_mock))

        with patch.object(TCellAgent, "get_agent", return_value=agent_mock):
            TCellAgent.request_metric("route-id",
                                      100,
                                      "remote_address",
                                      "user-agent",
                                      "session-id",
                                      "user-id")
            self.assertTrue(report_metrics_mock.called)
            self.assertEqual(report_metrics_mock.call_args_list,
                             [call(100,
                                   "route-id",
                                   "session-id",
                                   "user-id",
                                   "user-agent",
                                   "remote_address")])

    def test_discover_routes(self):
        discover_routes_mock = Mock()
        send_events_mock = Mock()
        agent_mock = Mock(route_table=PropertyMock(discover_routes=discover_routes_mock),
                          send_events=send_events_mock)

        with patch.object(TCellAgent, "get_agent", return_value=agent_mock):
            route_info = RouteInfo(route_url="route-url",
                                   route_method="route-method",
                                   route_target="route-target",
                                   route_id="route-id")
            TCellAgent.discover_routes([route_info])
            self.assertTrue(discover_routes_mock.called)
            self.assertEqual(discover_routes_mock.call_args_list,
                             [call([route_info], send_events_mock)])

    def test_discover_database_fields(self):
        discover_database_fields_mock = Mock()
        send_event_mock = Mock()
        agent_mock = Mock(route_table=PropertyMock(discover_database_fields=discover_database_fields_mock),
                          send_event=send_event_mock)

        with patch.object(TCellAgent, "get_agent", return_value=agent_mock):
            TCellAgent.discover_database_fields("db-name",
                                                "schema-name",
                                                "table-name",
                                                ["field"],
                                                "route-id")
            self.assertTrue(discover_database_fields_mock.called)
            self.assertEqual(discover_database_fields_mock.call_args_list,
                             [call("db-name",
                                   "schema-name",
                                   "table-name",
                                   ["field"],
                                   "route-id",
                                   send_event_mock)])
