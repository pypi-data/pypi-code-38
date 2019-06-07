'''
Configuration module holding the program's config data
and the root logger.
'''
import inspect
import json
import os
# from importlib import import_module
from pathlib import Path

import pkg_resources

import __main__

from .exceptions import ConfigError
from .logger import LOGGER


class ImplementationError(ConfigError):
    '''
    Error triggered when the configuration processing failed unexpectedly.
    '''

    def __init__(self, message, *errors):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        self.errors = errors


class ConfigAccessError(ConfigError):
    '''
    Error triggered when the configuration file can not be accessed.
    '''

    def __init__(self, message, *errors):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        self.errors = errors


class MissingConfig(ConfigError):
    '''
    Error triggered when the configuration file is missing.
    '''

    def __init__(self, message, *errors):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        self.errors = errors


class InvalidConfig(ConfigError):
    '''
    Error triggered when a parsing or validation error occurs.
    '''

    def __init__(self, message, *errors):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        self.errors = errors


class Config(dict):
    '''
    Configuration wrapper class that provides lazy initialization.
    '''

    def __init__(self, config=None):
        '''
        Initializes the inner configuration object if one is given. Otherwise, the first subscription will trigger the lazy
        loading mechanism.
        '''
        self.config = config

    def __getitem__(self, item):
        '''
        Makes the class subscribable.
        '''
        if object.__getattribute__(self, 'config') is None:
            object.__getattribute__(self, 'load')()
        return object.__getattribute__(self, 'config')[item]

    def __setitem__(self, key, value):
        # https://docs.python.org/3/library/exceptions.html#TypeError
        raise TypeError('Config objects should not be modified after loading. Please change your config file.')

    def __delitem__(self, key):
        # https://docs.python.org/3/library/exceptions.html#TypeError
        raise TypeError('Config objects should not be modified after loading. Please change your config file.')

    # def __getattribute__(self, name):
    #     if name == 'load':
    #         return object.__getattribute__(self, 'load')
    #     if object.__getattribute__(self, 'config') is None:
    #         object.__getattribute__(self, 'load')()
    #     try:
    #         return object.__getattribute__(self, 'config')[name]
    #     except AttributeError:
    #         raise ConfigAccessError(
    #             f'Invalid config attribute: {name}. Config:\n{repr(object.__getattribute__(self, "config"))}')

    def load(self, caller=None):
        '''
        Loads the config. Local files have precedence over asset files.

        :param caller: Used for the config file name template. If `None` the package name is inferred. (default: `None`)
        '''
        if caller is None:
            if __main__.__package__ is not None:
                caller = __main__.__package__
            else:
                index = 0
                caller = None
                while True:
                    index += 1
                    __frame = inspect.stack()[index]
                    __module = inspect.getmodule(__frame[0])
                    if __module is None:
                        break
                    caller = __module.__package__.split('.')[0]
                    if caller != __package__ or __module.__package__ == __package__ + '.tests':
                        break
                    caller = None

                if caller is None:
                    caller = __package__

        env_var = "MOZINTERMITTENT_{}_CONFIG".format(caller.upper())
        config_file = os.getenv(env_var)
        file_name = '{}.conf'.format(caller)

        # Environment variable not set.
        # Lookup usual file locations
        if config_file is None:
            locations = [Path('.'), Path.home(), Path('/etc')]
            LOGGER.warning('%s not set. Looking for config %s in %s',
                           env_var, file_name, [str(x) for x in locations])

            for location in locations:
                path = Path(location, file_name)
                LOGGER.debug("Checking %s", path)
                if path.is_file():
                    config_file = str(path)
                    break

        # Could not find config.
        # Create default config from assets and raise error.
        if config_file is None:
            path = Path(Path.home(), file_name)
            with open(path, 'wb') as cfile:
                LOGGER.warning(
                    'Creating default config. Please edit file %s', path)
                cfile.write(pkg_resources.resource_string(
                    caller, 'assets/{}.conf.example'.format(caller)))
            raise MissingConfig("Missing configuration file.", [])

        # Config was set but is not an (accessible) file.
        if not Path(config_file).is_file():
            raise MissingConfig(
                "Could not read config from {}. No such file.".format(config_file))

        # Read the configuration.
        with open(config_file, 'r') as cfile:
            LOGGER.info("Reading config from '%s'.", path)
            config_string = cfile.read()

            # Check if the file is valid JSON.
            try:
                temp_config = json.loads(config_string)
            except json.decoder.JSONDecodeError as err:
                raise InvalidConfig("Config is no valid JSON file.", err)

            # disabling parser generation for the moment
            # see https://gitlab.com/mozintermittent/python-libraries/gcshelpers/issues/4 for details.
            self.config = temp_config
            # # Generate parser and validate configuration
            # source = 'assets/{}.conf.jsg'.format(caller)

            # # Check if we need to validate the configuration against
            # # a defined schema in caller::assets/caller.conf.jsg
            # try:
            #     schema = pkg_resources.resource_string(caller, source)
            # except FileNotFoundError:
            #     # skip validation as the package does not provide a config schema
            #     self.config = temp_config
            #     return

            # # create the python class to parse the configuration
            # from pyjsg.parser_impl.generate_python import parse
            # python = parse(schema.decode('utf-8'), source)

            # # save the file
            # parser_name = '__config_parser_{}'.format(caller)
            # directory = os.path.dirname(inspect.getfile(globals()[caller])) if caller in globals(
            # ) else os.path.dirname(os.path.abspath(__file__))
            # source_file = directory + '/' + parser_name + '.py'
            # with open(source_file, 'w') as outfile:
            #     outfile.write(python)
            #     outfile.flush()
            #     # force persisting to disk
            #     os.fsync(outfile)

            # # load the parser and validate the configuration
            # try:
            #     config_parser = import_module('.'+parser_name, package=caller)
            #     os.remove(source_file)
            #     from pyjsg.jsglib.loader import loads
            #     v_config: config_parser.Schema = loads(
            #         config_string, config_parser)
            #     self.config = v_config

            #     # provide this class with the attributes of the configuration
            #     # this will clash if the top level document contains 'load'
            #     # for name in [x for x in self.config.__dict__.keys() if not x.startswith('_')]:
            #     #   setattr(Config, name, property(lambda x, name=name: x.config[name]))
            # except ModuleNotFoundError as err:
            #     raise ImplementationError(
            #         'Failed to create config parser.', err)
            # except ValueError as err:
            #     raise InvalidConfig('Could not validate config.', err)


CONFIG = Config()


def pkgload(package, path):
    '''
    Loads a file from the `assets` directory into a string.

    :param package: the name of the package the resource shall be loaded from.
    :param path: the path to the resource within the package.
    :return: the string representation of the loaded resource.
    '''
    return pkg_resources.resource_string(package, path)
