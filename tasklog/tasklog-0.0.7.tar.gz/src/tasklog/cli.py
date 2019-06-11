""" CLI Implementation

"""
from argparse import ArgumentParser
from inspect import getfullargspec
from logging import StreamHandler, FileHandler, Formatter
from sys import stdout
from pathlib import Path

from .__version__ import __version__
from .operations import jiraWorklogCommand
from .helper.config import config
from .helper.logger import logger
from .constants import EXIT_CODE_FAIL_GENERIC, EXIT_CODE_SUCCESS
from .commandexception import CommandException


def maincli(argv=None):
    """ CLI application entry point

    :param argv: argument list to parse
    """
    # Parse args
    args = _parseArguments(argv)

    # Load config options
    configFilePath = Path(args.config).resolve()
    config.load(str(configFilePath))
    # Log to console and file
    consoleFormatter = Formatter('%(asctime)s -  %(levelname)s - %(message)s')
    fileFormatter = Formatter('%(levelname)s - %(message)s')
    consoleHandler = StreamHandler(stdout)
    consoleHandler.setFormatter(consoleFormatter)
    logFilePath = Path(config.logging.file).resolve()
    fileHandler = FileHandler(filename=logFilePath)
    fileHandler.setFormatter(fileFormatter)

    logger.start(config.logging.severity, consoleHandler)
    logger.start(config.logging.severity, fileHandler)

    logger.debug("Configuration loaded")
    logger.info("Log file: {}".format(logFilePath))

    # Run requested command
    command = args.command
    args = vars(args)
    spec = getfullargspec(command)
    if not spec.varkw:
        # No kwargs, remove unexpected arguments.
        args = {key: args[key] for key in args if key in spec.args}

    args['config'] = config
    try:
        command(**args)
        return EXIT_CODE_SUCCESS
    except CommandException as exception:
        logger.critical("Command Error: {}. {}".format(exception.exitCode, exception.message))
        return exception.exitCode
    except RuntimeError as error:
        logger.critical("Runtime Error: {}.".format(error))
        return EXIT_CODE_FAIL_GENERIC


def _parseArguments(args):
    """ Parse command line arguments.

    :param args: argument list to parse
    """
    parser = ArgumentParser()

    # General purpose options
    parser.add_argument("-c", "--config", action="store",
                        help="Config file")

    parser.add_argument("-V", "--version", action="version",
                        version="{:s}".format(__version__),
                        help="Print version and exit")

    # General purpose options for all commands
    common = ArgumentParser(add_help=False)
    # common.add_argument("--name", "-n", default="World", help="greeting name")

    # Per command options
    subparsers = parser.add_subparsers(title="subcommands")
    _setupJIRAWorklogParser(subparsers, common)
    args = parser.parse_args(args)

    return args


def _setupJIRAWorklogParser(subparsers, common):
    """ Log tasklog to JIRA command parser

    :param subparsers: subcommand parsers
    :param common: parser for common subcommand arguments
    """
    parser = subparsers.add_parser("submit", parents=[common])
    parser.set_defaults(command=jiraWorklogCommand)

    parser.add_argument("-f", "--fromFilePath", action="store",
                        help="File with tasklogs to submit",
                        default="tasklogs.txt")

    return
