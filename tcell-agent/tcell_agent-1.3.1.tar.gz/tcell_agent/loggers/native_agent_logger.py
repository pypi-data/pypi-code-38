
from tcell_agent.rust.native_callers import NativeAgentCaller


NUMERIC_LEVEL_VALUES = {"debug": 10,
                        "info": 20,
                        "warn": 30,
                        "error": 40,
                        "critical": 50}


def level_to_numeric_value(level):
    level_lowercased = level.lower()
    return NUMERIC_LEVEL_VALUES.get(level_lowercased, 20)


class NativeAgentLogger(object):
    def __init__(self, agent_ptr, logging_options):
        self.logging_enabled = logging_options["enabled"]
        self.logging_level = level_to_numeric_value(logging_options["level"])
        self.agent_ptr = agent_ptr

    def should_log_message(self, level):
        numeric_level = level_to_numeric_value(level)
        return self.logging_enabled and numeric_level >= self.logging_level

    def log_message(self, level, message, module_name):
        if level and message and self.should_log_message(level):
            message_json = {
                "level": level,
                "message": message,
                "thread": module_name
            }
            caller = NativeAgentCaller(agent_ptr=self.agent_ptr,
                                       native_method_name="log_message",
                                       bytes_to_allocate=1024 * 8)
            caller.append_parameter(message_json)
            caller.execute()
