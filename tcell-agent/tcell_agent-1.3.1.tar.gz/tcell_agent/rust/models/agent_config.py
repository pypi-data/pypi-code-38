from tcell_agent.version import VERSION


class AgentConfig(dict):
    def __init__(self, configuration):
        dict.__init__(self)

        send_mode = "Normal"
        if configuration.demomode:
            send_mode = "Demo"

        self["disable_event_sending"] = not configuration.enable_event_manager
        self["send_mode"] = send_mode
        self["agent_type"] = "Python"
        self["agent_version"] = VERSION
        self["diagnostics_enabled"] = False
        self["application"] = {
            "app_id": configuration.app_id,
            "api_key":  configuration.api_key,
            "tcell_api_url": configuration.tcell_api_url,
            "tcell_input_url": configuration.tcell_input_url,
            "hmac_key": configuration.hmac_key,
            "password_hmac_key": configuration.password_hmac_key,
            "allow_payloads": configuration.allow_payloads,
            "js_agent_api_base_url": configuration.js_agent_api_base_url,
            "js_agent_url": configuration.js_agent_url,
            "cache_dir": configuration.cache_folder,
            "log_dir": configuration.log_directory,
            "logging_options": configuration.logging_options,
            "host_identifier": configuration.host_identifier,
            "reverse_proxy_ip_address_header": configuration.reverse_proxy_ip_address_header,
            "fetch_policies_from_tcell": configuration.fetch_policies_from_tcell
        }
        self["appfirewall"] = {
            "enable_body_json_inspection": True,
            "allow_log_payloads": True
        }
        self["max_header_size"] = configuration.max_csp_header_bytes or (1024 * 1024)
