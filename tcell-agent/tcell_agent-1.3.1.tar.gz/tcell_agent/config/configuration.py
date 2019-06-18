# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

import socket
import os
import os.path

from tcell_agent.config.logging_options import LoggingOptions


_CONFIGURATION = None


def get_config():
    return _CONFIGURATION


def set_config(config):
    global _CONFIGURATION  # pylint: disable=global-statement
    _CONFIGURATION = config


class TCellAgentConfiguration(object):
    """
    IMPORTANT:
    IMPORTANT: every time a config setting is added make sure to added to tcell_agent.config.unknown_options
    IMPORTANT:
    """
    def __init__(self):
        self.enabled = True
        self.enabled_instrumentations = {"django_auth": True}
        self.enable_event_manager = True
        self.fetch_policies_from_tcell = True
        self.app_id = None
        self.api_key = None
        self.allow_payloads = True
        self.tcell_api_url = "https://api.tcell.io/api/v1"
        self.tcell_input_url = "https://input.tcell.io/api/v1"
        self.js_agent_url = "https://jsagent.tcell.io/tcellagent.min.js"
        self.js_agent_api_base_url = None
        self.logging_options = LoggingOptions()
        self.host_identifier = socket.getfqdn()
        self.preload_policy_filename = None
        self.hmac_key = None
        self.password_hmac_key = None
        self.reverse_proxy = True
        self.reverse_proxy_ip_address_header = "X-Forwarded-For"
        self.max_csp_header_bytes = None
        self.demomode = False
        self.max_data_ex_db_records_per_request = 1000
        self.tcell_home = os.environ.get("TCELL_AGENT_HOME", "tcell/")
        self.cache_folder = os.path.join(self.tcell_home, "cache/")
        self.log_directory = os.environ.get("TCELL_AGENT_LOG_DIR", os.path.join(self.tcell_home, "logs/"))

    def read_config(self, config_json):
        if config_json.get("version") != 1:
            return

        applications = config_json.get("applications")
        if applications and len(applications) < 1:
            return

        app_config = applications[0]

        self.app_id = app_config.get("app_id")
        self.api_key = app_config.get("api_key")
        self.enabled = app_config.get("enabled", True)
        self.enable_event_manager = app_config.get("enable_event_manager", True)
        self.fetch_policies_from_tcell = app_config.get("fetch_policies_from_tcell", True)
        self.preload_policy_filename = app_config.get("preload_policy_filename")
        self.logging_options = LoggingOptions(app_config.get("logging_options"))
        self.log_directory = app_config.get("log_dir", self.log_directory)
        self.tcell_api_url = app_config.get("tcell_api_url", self.tcell_api_url)
        self.tcell_input_url = app_config.get("tcell_input_url", self.tcell_input_url)
        self.host_identifier = app_config.get("host_identifier", self.host_identifier)
        self.hmac_key = app_config.get("hmac_key", None)
        self.password_hmac_key = app_config.get("password_hmac_key", None)
        self.js_agent_url = app_config.get("js_agent_url", self.js_agent_url)
        max_csp_header_bytes = app_config.get("max_csp_header_bytes", None)
        if max_csp_header_bytes and max_csp_header_bytes > 0:
            self.max_csp_header_bytes = max_csp_header_bytes
        self.allow_payloads = app_config.get("allow_payloads", self.allow_payloads)
        data_exposure = app_config.get("data_exposure", {})
        self.max_data_ex_db_records_per_request = data_exposure.get("max_data_ex_db_records_per_request",
                                                                    self.max_data_ex_db_records_per_request)
        self.reverse_proxy = app_config.get("reverse_proxy", self.reverse_proxy)
        self.reverse_proxy_ip_address_header = app_config.get(
            "reverse_proxy_ip_address_header", self.reverse_proxy_ip_address_header)
        self.enabled_instrumentations = app_config.get("enabled_instrumentations", self.enabled_instrumentations)
        self.demomode = app_config.get("demomode", self.demomode)
        self.js_agent_api_base_url = app_config.get("js_agent_api_base_url", self.tcell_api_url)

    def load_env_vars(self):
        self.allow_payloads = os.environ.get("TCELL_AGENT_ALLOW_PAYLOADS", self.allow_payloads) in [True, "true", "1"]
        self.demomode = os.environ.get("TCELL_DEMOMODE", self.demomode) in [True, "true", "1"]
        self.app_id = os.environ.get("TCELL_AGENT_APP_ID", self.app_id)
        self.api_key = os.environ.get("TCELL_AGENT_API_KEY", self.api_key)
        self.host_identifier = os.environ.get("TCELL_AGENT_HOST_IDENTIFIER", self.host_identifier)
        self.tcell_input_url = os.environ.get("TCELL_INPUT_URL", self.tcell_input_url)
        self.hmac_key = os.environ.get("TCELL_HMAC_KEY", self.hmac_key)
        self.password_hmac_key = os.environ.get("TCELL_PASSWORD_HMAC_KEY", self.password_hmac_key)
        self.tcell_api_url = os.environ.get("TCELL_API_URL", self.tcell_api_url)
        self.js_agent_api_base_url = self.js_agent_api_base_url or self.tcell_api_url

    def should_instrument_django_auth(self):
        return self.enabled_instrumentations.get("django_auth", True) in [True, "true"]
