from tcell_agent.events.app_config_settings import AppConfigSettings


class SettingsEvent(AppConfigSettings):
    def __init__(self, name, value):
        if isinstance(value, bool):
            value = str(value).lower()

        super(SettingsEvent, self).__init__("tcell",
                                            "config",
                                            name=name,
                                            value=value)
