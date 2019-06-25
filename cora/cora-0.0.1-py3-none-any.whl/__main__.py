"""Cora command line entrypoint."""

import sys
import argparse
import logging

from cora.__about__ import __name__, __version__
from termcolor import colored

def main(arguments=None):
    """Parse arguments, start logging, and run."""
    if arguments == None:
        arguments = sys.argv[1:]

    argument_parser = argparse.ArgumentParser(

    )

    argument_parser.add_argument('-V', '--version',
        action='store_true',
        help='display version number and exit'
    )

    subparsers = argument_parser.add_subparsers(
        title='commands',
        metavar='<command>'
    )

    start_parser = subparsers.add_parser(
        name='start',
        help='start cora'
    )

    stop_parser = subparsers.add_parser(
        name='stop',
        help='stop cora'
    )

    restart_parser = subparsers.add_parser(
        name='restart',
        help='restart cora'
    )

    commands = argument_parser.parse_args(arguments)

    if commands.version:
        print(__name__.capitalize() + ' ' + __version__)

    try:
        commands.execute(commands)
    except AttributeError as error:
        logging.debug(colored(error, 'green'))

    exit()

if __name__ == '__main__':
    main()