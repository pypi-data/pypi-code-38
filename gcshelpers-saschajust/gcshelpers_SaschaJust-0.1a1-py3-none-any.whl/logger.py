'''
This module provides a logging object `LOGGER` that is eagerly initialized.
If no log configuration is present, one will be generated on the fly using
the sample configuration in `assets/log.conf.example`.
'''

import logging
import logging.config
import os
from pathlib import Path

import pkg_resources


class MozLogger:
    '''
    Wraps an instance of the root logger, featuring lazy loading of the log configuration.
    '''

    def __init__(self, logger: logging.Logger = None):
        self.logger = logger

    def __getattribute__(self, name):
        if object.__getattribute__(self, 'logger') is None:
            object.__getattribute__(self, 'load')()
        return object.__getattribute__(object.__getattribute__(self, 'logger'), name)

    def load(self):
        '''
        Loads the log config. Provides a default config if the config cannot be found.
        '''
        env_var = "MOZINTERMITTENT_{}_LOGCONF".format(__package__.upper())
        config_file = os.getenv(env_var)
        name = "{}_log.conf".format(__package__)
        if config_file is None:
            locations = [Path('.', 'log.conf'), Path('.', name), Path(
                Path.home(), name), Path('/etc', name)]
            for location in locations:
                if location.is_file():
                    config_file = str(location)
                    break

        # make sure there is a log configuration
        if config_file is None:
            config_file = str(Path('.', name))
            with open(config_file, 'wb') as cfile:
                try:
                    config_str = pkg_resources.resource_string(
                        __package__, 'assets/log.conf.example')
                except FileNotFoundError:
                    config_str = pkg_resources.resource_string(
                        'gcshelpers', 'assets/log.conf.example')

                cfile.write(config_str)

        logging.config.fileConfig(config_file)
        self.logger = logging.getLogger(__package__)
        # for method in [method_name for method_name in dir(self.logger) if not method_name.startswith('_') and callable(getattr(self.logger, method_name))]:
        #   func = self.logger.__class__.__getattribute__(self.logger, method)
        #   f2 = partial(MozLogger.guard, self, func)
        #   MozLogger.__class__.__setattr__(MozLogger, method, f2)


LOGGER = MozLogger()
