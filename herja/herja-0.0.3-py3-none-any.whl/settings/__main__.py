"""Execute a reset, a get, or a set command for various settings."""


import os

from . import Settings, SETTINGS_PATH
from ..decorators import MainCommands
from ..logging import get_logger


LOGGER = get_logger()


@MainCommands(
    ('reset', 'Reset the configuration settings by deleting the settings file.', []),
    ('get', 'Get a value from stored settings.', [
        (['key'], {'help': 'The name of the value to obtain from settings.'})
    ]),
    ('set', 'Set a value to be stored in settings.', [
        (['key'], {'help': 'The name of the value to save in settings.'}),
        (['value'], {'help': 'The value of the key to be stored in settings.'})
    ]),
    ('enum', 'List the values currently stored.', []),
    ('prompt', 'Prompt the user for a value to be saved.', [
        (['key'], {'help': 'The name of the value to save in settings.'})
    ])
)
def main(args):
    """Handle arguments given to this module."""
    # remove the current configuration file, if it exists
    if args.command == 'reset':
        LOGGER.info('Ensuring log does not exist: "%s"', SETTINGS_PATH)
        if os.path.isfile(SETTINGS_PATH):
            LOGGER.info('Removing log: "%s"', SETTINGS_PATH)
            os.remove(SETTINGS_PATH)

    # get a configuration value
    if args.command == 'get':

        # read the setting
        with Settings() as settings:
            result = settings[args.key]
        LOGGER.info('Settings key "%s" has value "%s".', args.key, result)

    # set a configuration value
    if args.command == 'set':
        if args.value.isdigit():
            args.value = int(args.value)

        with Settings() as settings:
            settings[args.key] = args.value

        # check it was written correctly
        with Settings() as settings:
            result = settings.get(args.key, None)

        assert result == args.value, 'Invalid result obtained: "{0}"'.format(result)

    # enumerate the settings
    if args.command == 'enum':
        with Settings() as settings:
            print('[Settings]')
            for key in settings:
                print('{0}={1}'.format(key, settings[key]))
            print()

    return 0
