from __future__ import unicode_literals

import os


def get_unknown_options(config_json):
    messages = []

    known_tcell_env_vars = set([
        "TCELL_AGENT_ALLOW_PAYLOADS",
        "TCELL_AGENT_ALLOW_UNENCRYPTED_APPSENSOR_PAYLOADS",
        "TCELL_AGENT_ALLOW_UNENCRYPTED_APPFIREWALL_PAYLOADS",
        "TCELL_DEMOMODE",
        "TCELL_AGENT_HOME",
        "TCELL_AGENT_LOG_DIR",
        "TCELL_AGENT_CONFIG",
        "TCELL_AGENT_APP_ID",
        "TCELL_AGENT_API_KEY",
        "TCELL_AGENT_HOST_IDENTIFIER",
        "TCELL_INPUT_URL",
        "TCELL_HMAC_KEY",
        "TCELL_API_URL",
        "TCELL_PASSWORD_HMAC_KEY"
    ])

    for environment_key in os.environ.keys():
        if environment_key.startswith("TCELL_") and environment_key not in known_tcell_env_vars:
            messages.append("Unrecognized environment parameter (TCELL_*) found: {env_var}".format(env_var=environment_key))

    try:
        key_differences = set()
        if config_json:
            first_level_keys = set(["version", "COMPANY", "APP_NAME", "API_KEY", "TCELL_INPUT_URL", "applications"])

            key_differences = set(config_json.keys()) - first_level_keys

            applications = config_json.get("applications")
            if applications:

                if len(applications) > 1:
                    messages.append("Multiple applications detected in config file")

                elif len(applications) == 1:
                    application = applications[0]

                    application_keys = set([
                        "enabled",
                        "name",
                        "app_id",
                        "api_key",
                        "fetch_policies_from_tcell",
                        "preload_policy_filename",
                        "log_dir",
                        "tcell_api_url",
                        "tcell_input_url",
                        "host_identifier",
                        "hmac_key",
                        "password_hmac_key",
                        "js_agent_api_base_url",
                        "js_agent_url",
                        "max_csp_header_bytes",
                        "allow_unencrypted_appsensor_payloads",
                        "allow_unencrypted_appfirewall_payloads",
                        "allow_payloads",
                        "reverse_proxy",
                        "reverse_proxy_ip_address_header",
                        "demomode",
                        "company",
                        "logging_options",
                        "data_exposure",
                        "enabled_instrumentations"])

                    key_differences = key_differences.union(set(application.keys()) - application_keys)

                    if "logging_options" in application:
                        logging_options = application["logging_options"]
                        key_differences = key_differences.union(set(logging_options.keys()) - set(["enabled", "level", "filename"]))

                    if "data_exposure" in application:
                        data_exposure = application["data_exposure"]
                        key_differences = key_differences.union(set(data_exposure.keys()) - set(["max_data_ex_db_records_per_request"]))

                    if "enabled_instrumentations" in application:
                        enabled_instrumentations = application["enabled_instrumentations"]
                        key_differences = key_differences.union(set(enabled_instrumentations.keys()) - set(["django_auth"]))

        for k in key_differences:
            messages.append("Unrecognized config setting key: {k}".format(k=k))

    except Exception as exception:
        messages.append("Something went wrong verifying config file: {e}".format(e=exception))

    return messages
