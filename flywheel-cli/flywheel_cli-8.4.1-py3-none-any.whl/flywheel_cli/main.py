#!/usr/bin/env python3
import argparse
import logging
import os
import platform
import sys

import flywheel

from .commands import add_commands
from . import monkey, util

log = logging.getLogger(__name__)
perror = util.perror


def main():
    # Handle fs weirdness
    monkey.patch_fs()

    # Disable terminal colors if NO_COLOR is set
    if os.environ.get('NO_COLOR'):
        import crayons
        crayons.disable()

    # Global exception handler for KeyboardInterrupt
    sys.excepthook = ctrlc_excepthook

    # Create base parser and subparsers
    parser = argparse.ArgumentParser(prog='fw', description='Flywheel command-line interface')

    # Add commands from commands module
    add_commands(parser)

    # Parse arguments
    args = parser.parse_args()

    # Additional configuration
    config_fn = getattr(args, 'config', None)
    if callable(config_fn):
        config_fn(args)

    log.debug('CLI Version: %s', util.get_cli_version())
    log.debug('CLI Args: %s', sys.argv)
    log.debug('Platform: %s', platform.platform())
    log.debug('System Encoding: %s', sys.stdout.encoding)
    log.debug('Python Version: %s', sys.version)

    func = getattr(args, 'func', None)
    if func is not None:
        # Invoke command
        try:
            rc = args.func(args)
            if rc is None:
                rc = 0
        except flywheel.ApiException as e:
            log.debug('Uncaught ApiException', exc_info=True)
            if e.status == 401:
                perror('You are not authorized: {}'.format(e.detail or 'unknown reason'))
                perror('Maybe you need to refresh your API key and login again?')
            else:
                perror('Request failed: {}'.format(e.detail or e))
            rc = 1
        except Exception as e:
            log.debug('Uncaught Exception', exc_info=True)
            perror('Error: {}'.format(e))
            rc = 1
    else:
        parser.print_help()
        rc = 1

    sys.exit(rc)

def ctrlc_excepthook(exctype, value, traceback):
    if exctype == KeyboardInterrupt:
        perror('\nUser cancelled execution (Ctrl+C)')
        logging.getLogger().setLevel(100) # Supress any further log output
        os._exit(1)
    else:
        sys.__excepthook__(exctype, value, traceback)

if __name__ == '__main__':
    main()
