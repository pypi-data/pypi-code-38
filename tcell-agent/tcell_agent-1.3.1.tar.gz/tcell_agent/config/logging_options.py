from tcell_agent.utils.strings import ensure_string

ALLOWED_LEVELS = {
    "DEBUG": "DEBUG",
    "INFO": "INFO",
    "WARN": "WARN",
    "ERROR": "ERROR",
    "CRITICAL": "CRITICAL"
}


class LoggingOptions(dict):
    def __init__(self, options=None):
        super(LoggingOptions, self).__init__()

        if options is None:
            options = {}

        self["enabled"] = options.get("enabled") in [None, True]
        self["level"] = ALLOWED_LEVELS.get(options.get("level")) or "INFO"
        self["filename"] = ensure_string(options.get("filename") or "tcell_agent.log")
