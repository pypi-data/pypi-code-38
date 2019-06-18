from __future__ import unicode_literals

import os
import unittest

from tcell_agent.config.unknown_options import get_unknown_options


class TcellAgentConfigurationTest(unittest.TestCase):

    def test_check_env_for_unknown_flags(self):
        # save environment keys
        saved_environment_keys = {
            environment_key: os.environ[environment_key]
            for environment_key in list(os.environ.keys())
            if environment_key.startswith("TCELL_")
        }

        os.environ["TCELL_HACK"] = "hack the system"
        os.environ["TCELL_AGENT_ALLOW_UNENCRYPTED_APPSENSOR_PAYLOADS"] = "valid"
        os.environ["TCELL_AGENT_ALLOW_UNENCRYPTED_APPFIREWALL_PAYLOADS"] = "valid"
        os.environ["TCELL_DEMOMODE"] = "valid"
        os.environ["TCELL_AGENT_HOME"] = "valid"
        os.environ["TCELL_AGENT_LOG_DIR"] = "valid"
        os.environ["TCELL_AGENT_CONFIG"] = "valid"
        os.environ["TCELL_AGENT_APP_ID"] = "valid"
        os.environ["TCELL_AGENT_API_KEY"] = "valid"
        os.environ["TCELL_AGENT_HOST_IDENTIFIER"] = "valid"
        os.environ["TCELL_INPUT_URL"] = "valid"
        os.environ["TCELL_HMAC_KEY"] = "valid"
        os.environ["TCELL_API_URL"] = "valid"
        os.environ["TCELL_PASSWORD_HMAC_KEY"] = "valid"

        messages = get_unknown_options(None)

        # remove test data
        for environment_key in list(os.environ.keys()):
            if environment_key.startswith("TCELL_"):
                del os.environ[environment_key]

        # restore saved_environment_keys
        for environment_key in saved_environment_keys:
            os.environ[environment_key] = saved_environment_keys[environment_key]

        self.assertEqual(messages, ["Unrecognized environment parameter (TCELL_*) found: TCELL_HACK"])

    def test_check_config_json_for_unknown_options(self):
        config_json = {
            "first_level": "boo",
            "version": 1,
            "COMPANY": "co",
            "APP_NAME": "app name",
            "API_KEY": "api key",
            "TCELL_INPUT_URL": "tcell input url",
            "applications": [{
                "second_level": "boo",
                "enabled": True,
                "name": "name",
                "app_id": "app id",
                "api_key": "api key",
                "fetch_policies_from_tcell": True,
                "preload_policy_filename": "preload policy filename",
                "log_dir": "custom log dir",
                "logging_options": {
                    "logging_level": "boo",
                    "enabled": True,
                    "level": "DEBUG",
                    "filename": "filename"},
                "tcell_api_url": "tcell api url",
                "tcell_input_url": "tcell input url",
                "host_identifier": "host identifier",
                "hmac_key": "hmac key",
                "password_hmac_key": "password hmac key",
                "js_agent_api_base_url": "js agent api base url",
                "js_agent_url": "js agent url",
                "max_csp_header_bytes": 512,
                "allow_unencrypted_appsensor_payloads": True,
                "allow_unencrypted_appfirewall_payloads": True,
                "allow_payloads": True,
                "data_exposure": {
                    "data_ex_level": "boo",
                    "max_data_ex_db_records_per_request": 10000},
                "reverse_proxy": True,
                "reverse_proxy_ip_address_header": "reverse proxy ip address header",
                "demomode": True,
                "enabled_instrumentations": {
                    "enabled_instrumentations_level": "boo",
                    "django_auth": True},
                "company": "co"}]}

        messages = get_unknown_options(config_json)

        self.assertEqual(
            sorted(messages),
            ["Unrecognized config setting key: data_ex_level",
             "Unrecognized config setting key: enabled_instrumentations_level",
             "Unrecognized config setting key: first_level",
             "Unrecognized config setting key: logging_level",
             "Unrecognized config setting key: second_level"])

    def test_multiple_apps_unknown_options(self):
        config_json = {"applications": [{}, {}]}

        messages = get_unknown_options(config_json)

        self.assertEqual(
            messages,
            ["Multiple applications detected in config file"])
