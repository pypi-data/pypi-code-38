from tcell_agent.rust.native_callers import NativeCaller
from tcell_agent.rust.native_library import get_native_lib


def test_event_sender(config, events, version, uuid):
    if get_native_lib():
        caller = NativeCaller(native_method_name="test_event_sender",
                              bytes_to_allocate=1024 * 8)
        caller.append_parameter({
            "uuid":            uuid,
            "hostname":        config.host_identifier,
            "agent_type":      "Python",
            "agent_version":   version,
            "app_id":          config.app_id,
            "api_key":         config.api_key,
            "tcell_input_url": config.tcell_input_url,
            "events":          events
        })
        response = caller.execute()
        return response.get_errors()

    return []


def test_policies(config):
    if get_native_lib():
        caller = NativeCaller(native_method_name="test_policies",
                              bytes_to_allocate=1024 * 8)
        caller.append_parameter({
            "app_id":        config.app_id,
            "api_key":       config.api_key,
            "tcell_api_url": config.tcell_api_url
        })
        response = caller.execute()
        return response.get_errors()

    return []
