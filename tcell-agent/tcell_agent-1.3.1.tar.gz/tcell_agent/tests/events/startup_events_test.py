import unittest

from mock import patch

from tcell_agent.config.logging_options import LoggingOptions
from tcell_agent.events.startup_events import get_startup_events
from tcell_agent.tests.support.builders import ConfigurationBuilder
from tcell_agent.tests.support.context_library import ConfigContext


class TestPackage(object):
    def __init__(self, key, version):
        self.key = key
        self.version = version


class GetStartupEventsTest(unittest.TestCase):
    def test_get_startup_events(self):
        config = ConfigurationBuilder().update_attribute(
            "log_directory", "log-directory"
        ).update_attribute(
            "allow_payloads", True
        ).update_attribute(
            "reverse_proxy", True
        ).update_attribute(
            "logging_options", LoggingOptions()
        ).update_attribute(
            "hmac_key", "hmac-key"
        ).update_attribute(
            "reverse_proxy_ip_address_header", "X-Forwarded-For"
        ).update_attribute(
            "config_filename", "tcell_agent.config"
        ).build()
        packages = [TestPackage("tcell-agent", "1.0.0")]

        with patch("tcell_agent.events.server_agent_details.current_username",
                   return_value="user-name") as patched_current_username:
            with patch("tcell_agent.events.server_agent_details.current_group_id",
                       return_value="group-id") as patched_current_group_id:
                with patch("tcell_agent.events.server_agent_details.python_version_string",
                           return_value="3.6.5 (default, May  5 2018, 03:09:35) ") as patched_python_version_string:
                    with patch("tcell_agent.events.startup_events.get_packages",
                               return_value=packages) as patched_get_packages:
                        with ConfigContext(config):
                            initial_events = get_startup_events()

                        self.assertTrue(patched_get_packages.called)
                        self.assertTrue(patched_current_username.called)
                        self.assertTrue(patched_current_group_id.called)
                        self.assertTrue(patched_python_version_string.called)
                        self.assertEqual(
                            initial_events,
                            [
                                {"event_type": "server_agent_packages", "packages": [{"n": "tcell-agent", "v": "1.0.0"}]},
                                {"event_type": "server_agent_details", "user": "user-name", "group": "group-id", "language": "Python", "language_version": "3.6.5 (default, May  5 2018, 03:09:35) "},
                                {"event_type": "app_config_setting", "package": "tcell", "section": "config", "name": "logging_directory", "value": "log-directory"},
                                {"event_type": "app_config_setting", "package": "tcell", "section": "config", "name": "allow_payloads", "value": "true"},
                                {"event_type": "app_config_setting", "package": "tcell", "section": "config", "name": "logging_enabled", "value": "true"},
                                {"event_type": "app_config_setting", "package": "tcell", "section": "config", "name": "logging_level", "value": "info"},
                                {"event_type": "app_config_setting", "package": "tcell", "section": "config", "name": "logging_filename", "value": "tcell_agent.log"},
                                {"event_type": "app_config_setting", "package": "tcell", "section": "config", "name": "hmac_key_present", "value": "true"},
                                {"event_type": "app_config_setting", "package": "tcell", "section": "config", "name": "reverse_proxy", "value": "true"},
                                {"event_type": "app_config_setting", "package": "tcell", "section": "config", "name": "reverse_proxy_ip_address_header", "value": "x-forwarded-for"},
                                {"event_type": "app_config_setting", "package": "tcell", "section": "config", "name": "config_filename", "value": "tcell_agent.config"},
                                {"event_type": "app_config_setting", "package": "tcell", "section": "config", "name": "native_lib_loaded", "value": "true"}
                            ]
                        )
