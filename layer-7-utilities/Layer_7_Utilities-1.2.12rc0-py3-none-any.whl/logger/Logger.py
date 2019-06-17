import os
import json


class LoggerConfig(object):
    def __init__(
        self,
        __dsn__=None,
        __app_name__="_DefaultName",
        __version__="0.0.0",
        logspath="/opt/skynet/RedditBots/logs/",
        raven=True,
    ):

        configfilepath = os.path.join(os.path.dirname(__file__), "logging_config.json")
        with open(configfilepath, "rt") as f:
            self.config = json.load(f)

        # Replaces the filename with one specific to each bot
        try:
            self.config["handlers"]["rotateFileHandler"][
                "filename"
            ] = f"{logspath}_DefaultName_Logs.log".replace(
                "_DefaultName", __app_name__.replace(" ", "_")
            )
        except Exception:
            raise AttributeError("Unable to set normal logging configuration location")

        try:
            self.config["handlers"]["rotateFileHandler_debug"][
                "filename"
            ] = f"{logspath}_DefaultName_Logs_Debug.log".replace(
                "_DefaultName", __app_name__
            )
        except Exception:
            raise AttributeError("Unable to set debug logging configuration location")

        # If Raven (legacy) Sentry.io handler is enabled, set that config up
        if raven:
            # Add the Sentry handler:
            self.config["handlers"]["SentryHandler"] = {
                "level": "ERROR",
                "class": "raven.handlers.logging.SentryHandler",
                "dsn": __dsn__,
                "release": __version__,
            }

            # Enable the Sentry Handler in the main handlers
            self.config["loggers"]["root"]["handlers"] = [
                "consoleHandler",
                "rotateFileHandler",
                "rotateFileHandler_debug",
                "SentryHandler",
            ]

    def get_config(self):
        return self.config
