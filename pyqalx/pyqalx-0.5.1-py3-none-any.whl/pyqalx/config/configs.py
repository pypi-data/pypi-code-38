import configparser
import os
from inspect import ismodule
from os import environ

from . import defaults
from pyqalx.config.defaults import bots
from pyqalx.core.errors import QalxConfigProfileNotFound, QalxConfigFileNotFound


class Config(dict):
    key_prefix = ""
    filename = ""
    BOOLEAN_STATES = {'1': True, 'yes': True, 'true': True, 'on': True,
                      '0': False, 'no': False, 'false': False, 'off': False,
                      True: True, False: False}

    def __init__(self):
        dict.__init__(self, self.defaults)
        for key, value in [(k, v) for k, v in environ.items() if k.startswith(self.key_prefix)]:
            self[key.replace(self.key_prefix, "")] = value
        self.config_path = os.path.join(os.path.expanduser('~'), self.filename)

    def from_inifile(self, profile_name="default"):
        if os.path.exists(self.config_path):
            config = configparser.ConfigParser()
            config.optionxform = str
            with open(self.config_path) as cfg:
                config.read_string(cfg.read())  # this makes mocks easier over config.read(filepath)
            if profile_name in config.keys():
                config_dict = config[profile_name]
                self.update(config_dict)
            else:
                profiles = '\n'.join(config.keys())
                msg = "Couldn't find profile named {} in {} file." \
                      " Did you mean one of:\n{}".format(profile_name,
                                                         self.filename,
                                                         profiles)
                raise QalxConfigProfileNotFound(msg)
        else:
            raise QalxConfigFileNotFound("Couldn't find {}".format(self.config_path))

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, dict.__repr__(self))

    def getboolean(self, key):
        """
        Helper method for allowing us to handle multiple boolean values
        """
        # Convert to a string in case we're being given a python bool()
        value = str(self[key])
        if value.lower() not in self.BOOLEAN_STATES:
            raise ValueError('Not a boolean: %s' % value)
        return self.BOOLEAN_STATES[value.lower()]

    @property
    def defaults(self):

        return {k: v for k, v in vars(defaults).items() if (not k.startswith("__")) and (not ismodule(v))}


class BotConfig(Config):
    """Works exactly like a dict but provides ways to fill it from ini files
    and environment variables.  There are two common patterns to populate the
    config.
    Either you can add them to the `.bots` file:
        bot.config.from_botsfile(profile_name="default")
    Or alternatively you can define the configuration from environment variables
    starting with `QALX_BOT_`. These will be populated automatically
    but values defined in `.bots` will overwrite these if `bot.config.from_botsfile()` is called.
    To set environment variables before launching the application you have to set this
    environment variable to the name and value you want to use.  On Linux and OS X
    use the export statement::
        export QALX_BOT_LICENCE_FILE='/path/to/licence/file'
    On windows use `set` instead.
    :param defaults: an optional dictionary of default values
    """
    key_prefix = "QALX_BOT_"
    filename = ".bots"

    @property
    def defaults(self):
        config = super(BotConfig, self).defaults
        bot_config = {k: v for k, v in vars(bots).items() if not k.startswith("__") and (not ismodule(v))}
        config.update(bot_config)
        return config


class UserConfig(Config):
    """Works exactly like a dict but provides ways to fill it from ini files
    and environment variables.  There are two common patterns to populate the
    config.
    Either you can add them to the `.qalx_bot` file:
        qalx_bot.config.from_qalxfile(profile_name="default")
    Or alternatively you can define the configuration from environment variables
    starting with `QALX_USER_`. These will be populated automatically
    but values defined in `.bots` will overwrite these if `qalx_bot.config.from_qalxfile()` is called.
    To set environment variables before launching the application you have to set this
    environment variable to the name and value you want to use.  On Linux and OS X
    use the export statement::
        export QALX_USER_EMPLOYEE_NUMBER=1280937
    On windows use `set` instead.
    :param defaults: an optional dictionary of default values
    """
    key_prefix = "QALX_USER_"
    filename = ".qalx"
