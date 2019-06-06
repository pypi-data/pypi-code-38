# Copyright 2013-2017 PhishMe, Inc.  All rights reserved.
#
# This software is provided by PhishMe, Inc. ("PhishMe") on an "as is" basis and any express or implied warranties,
# including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
# disclaimed in all aspects.  In no event will PhishMe be liable for any direct, indirect, special, incidental or
# consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
# this software is pursuant to, and permitted only in accordance with, the agreement between you and PhishMe.

import logging
import logging.handlers
import sys

from . import PhishMeIntelligence, read_args, read_config

__email__ = 'support@phishme.com'

if __name__ == '__main__':

    # Description.
    SCRIPT_DESCRIPTION = ('This script will retrieve threat intelligence from PhishMe\'s API.'
                          'Documentation is publicly available at '
                          'https://www.threathq.com/documentation/display/MAD/Reference.')

    # Read input arguments.
    ARGS = read_args(SCRIPT_DESCRIPTION)

    # Read config file.
    CONFIG = read_config(ARGS.config_file)

    # Create logger and set default logging level.
    LOGGER = logging.getLogger()

    # Valid logging levels.
    valid_logging_levels = ['debug', 'info', 'warning', 'error']
    current_logging_level = CONFIG.get('local_log', 'log_level')
    if current_logging_level in valid_logging_levels:
        if current_logging_level == 'debug':
            LOGGER.setLevel(logging.DEBUG)
        elif current_logging_level == 'info':
            LOGGER.setLevel(logging.INFO)
        elif current_logging_level == 'warning':
            LOGGER.setLevel(logging.WARNING)
        elif current_logging_level == 'error':
            LOGGER.setLevel(logging.ERROR)
    else:
        print('Please set an appropriate logging level in config.ini, section \'local_log\', key \'log_level\'.')
        print('The following values are acceptable: ' + str(valid_logging_levels))
        print('Exiting.')
        sys.exit(1)

    # Create a RotatingFileHandler and set the formats.
    try:
        HANDLER = logging.handlers.RotatingFileHandler(CONFIG.get('local_log', 'log_file'), maxBytes=5 * 1024 * 1024, backupCount=9)
        FORMAT = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M.%S')
        HANDLER.setFormatter(FORMAT)
        LOGGER.addHandler(HANDLER)
    except (IOError, OSError):
        print('Could not access log file at: ' + CONFIG.get('local_log', 'log_file') + '. This is most likely a permissions issue.')

    # Instantiate a PhishMe Intelligence library.
    pm = PhishMeIntelligence(config=CONFIG, config_file_location=ARGS.config_file)

    # Perform a synchronization integration, as determined by the config.ini settings.
    pm.sync()
