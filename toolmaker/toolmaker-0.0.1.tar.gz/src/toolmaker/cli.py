#


""" Command line interface """


import argparse
import configparser
import logging
import pathlib

from . import core
from . import meta


def _create_args_parser(default_config_path, tools_names=None):
    args_parser = argparse.ArgumentParser(
        allow_abbrev=False,
    )
    args_parser.add_argument(
        '--version',
        action='version',
        version=meta.VERSION,
    )
    args_parser.add_argument(
        '--config', '-c',
        default=str(default_config_path),
        type=argparse.FileType('r'),
    )
    action_group = args_parser.add_mutually_exclusive_group()
    action_group.add_argument(
        '--build', '-b',
        action='store_true',
    )
    action_group.add_argument(
        '--rebuild', '-r',
        action='store_true',
    )
    action_group.add_argument(
        '--delete', '-d',
        action='store_true',
    )
    tools_group = args_parser.add_mutually_exclusive_group(required=True)
    tools_group.add_argument(
        '--all', '-a',
        action='store_true',
    )
    tools_group.add_argument(
        '--tools', '-t',
        choices=tools_names,
        metavar='tool',
        nargs='+',
    )
    return args_parser


def main():
    """ CLI main function
    """
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

    cwd_path = pathlib.Path.cwd()
    default_config_path = cwd_path.joinpath('toolmaker.cfg')

    args_parser = _create_args_parser(default_config_path)
    args = args_parser.parse_args()

    config = None
    if args.config:
        logger.info("Reading configuration from file '%s'", args.config)
        config = configparser.ConfigParser()
        try:
            config.read_file(args.config)
        except configparser.Error as config_error:
            args_parser.error(config_error)
    tools_names = config.sections()

    if not args.all:
        args_parser = _create_args_parser(default_config_path, tools_names)
        args = args_parser.parse_args()

    if args.tools:
        tools_names = args.tools

    if args.delete:
        core.delete(cwd_path, config, tools_names)
    elif args.rebuild:
        core.build(cwd_path, config, tools_names, force=True)
    else:
        core.build(cwd_path, config, tools_names)


# EOF
