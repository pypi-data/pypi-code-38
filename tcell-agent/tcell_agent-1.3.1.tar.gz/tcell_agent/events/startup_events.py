from tcell_agent.config.configuration import get_config
from tcell_agent.instrumentation.decorators import safe_wrap_function
from tcell_agent.rust.native_agent import get_native_lib
from tcell_agent.events.server_agent_packages import ServerAgentPackagesEvent
from tcell_agent.events.server_agent_details import ServerAgentDetailsEvent
from tcell_agent.events.settings_event import SettingsEvent
from tcell_agent.system_info import get_packages


def add_packages_event(initial_events):
    sape = ServerAgentPackagesEvent()
    for package in get_packages():
        sape.add_package(package.key, package.version)
    initial_events.append(sape)


def get_startup_events():
    initial_events = []
    config = get_config()
    safe_wrap_function(
        "Create ServerAgentPackagesEvent",
        add_packages_event,
        initial_events
    )
    safe_wrap_function(
        "Create ServerAgentDetailsEvent",
        lambda: initial_events.append(ServerAgentDetailsEvent())
    )
    safe_wrap_function(
        "SettingsEvent: logging_directory",
        lambda: initial_events.append(SettingsEvent("logging_directory", config.log_directory))
    )
    safe_wrap_function(
        "SettingsEvent: allow_payloads",
        lambda: initial_events.append(SettingsEvent("allow_payloads", config.allow_payloads))
    )

    logging_options = config.logging_options
    safe_wrap_function(
        "SettingsEvent: logging_enabled",
        lambda: initial_events.append(SettingsEvent("logging_enabled", config.reverse_proxy))
    )
    safe_wrap_function(
        "SettingsEvent: logging_level",
        lambda: initial_events.append(SettingsEvent("logging_level", logging_options["level"]))
    )
    safe_wrap_function(
        "SettingsEvent: logging_filename",
        lambda: initial_events.append(SettingsEvent("logging_filename", logging_options["filename"]))
    )
    safe_wrap_function(
        "SettingsEvent: hmac_key_present",
        lambda: initial_events.append(SettingsEvent("hmac_key_present", bool(config.hmac_key)))
    )
    safe_wrap_function(
        "SettingsEvent: reverse_proxy",
        lambda: initial_events.append(SettingsEvent("reverse_proxy", config.reverse_proxy))
    )
    safe_wrap_function(
        "SettingsEvent: reverse_proxy_ip_address_header",
        lambda: initial_events.append(SettingsEvent("reverse_proxy_ip_address_header", config.reverse_proxy_ip_address_header))
    )
    safe_wrap_function(
        "SettingsEvent: config_filename",
        lambda: initial_events.append(SettingsEvent("config_filename", config.config_filename))
    )
    safe_wrap_function(
        "SettingsEvent: native_lib_loaded",
        lambda: initial_events.append(SettingsEvent("native_lib_loaded", get_native_lib() is not None))
    )

    return initial_events
