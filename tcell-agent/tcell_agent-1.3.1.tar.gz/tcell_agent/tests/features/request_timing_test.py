import unittest
import datetime

from mock import Mock, call, patch

from tcell_agent.agent import TCellAgent
from tcell_agent.features.request_timing import end_timer
from tcell_agent.tests.support.builders import ContextBuilder


class EndTimerTest(unittest.TestCase):
    def test_no_start_time_timer(self):
        context = ContextBuilder().update_attribute(
            "start_time", 0
        ).build()

        request = Mock(_tcell_context=context)
        logger_mock = Mock(debug=Mock())
        with patch("tcell_agent.features.request_timing.get_current_time") as patched_get_current_time:
            with patch.object(TCellAgent, "request_metric") as patched_request_metric:
                with patch("tcell_agent.features.request_timing.get_module_logger",
                           return_value=logger_mock):
                    end_timer(request)

                    self.assertFalse(patched_get_current_time.called)
                    self.assertFalse(patched_request_metric.called)
                    self.assertFalse(logger_mock.debug.called)

    def test_end_timer(self):
        start_timestamp = 1456080000
        start_datetime = datetime.datetime.fromtimestamp(start_timestamp)
        end_datetime = datetime.datetime.fromtimestamp(start_timestamp + 1)
        context = ContextBuilder().update_attribute(
            "start_time", start_datetime
        ).update_attribute(
            "route_id", "route-id"
        ).update_attribute(
            "remote_address", "1.1.1.1"
        ).update_attribute(
            "user_agent", "user-agent"
        ).update_attribute(
            "session_id", "session-id"
        ).update_attribute(
            "user_id", "user-id"
        ).update_attribute(
            "path", "/path"
        ).build()

        request = Mock(_tcell_context=context)
        logger_mock = Mock(debug=Mock())
        with patch("tcell_agent.features.request_timing.get_current_time",
                   return_value=end_datetime):
            with patch.object(TCellAgent, "request_metric") as patched_request_metric:
                with patch("tcell_agent.features.request_timing.get_module_logger",
                           return_value=logger_mock):
                    end_timer(request)

                    self.assertTrue(patched_request_metric.called)
                    self.assertTrue(logger_mock.debug.called)
                    self.assertEqual(patched_request_metric.call_args_list,
                                     [call("route-id",
                                           1000,
                                           "1.1.1.1",
                                           "user-agent",
                                           "session-id",
                                           "user-id")])
                    self.assertEqual(logger_mock.debug.call_args_list,
                                     [call("/path request took 1000")])
