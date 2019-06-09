import typing

import sloth_cli
from sloth_cli import parsing
from sloth_cli import profiler


def show_version(**kwargs):
    """Displays the current version"""

    print('sloth-cli Version {}'.format(sloth_cli.__version__))
    return sloth_cli.__version__


def show_help():
    """Displays the command help and exits"""
    parsing.parse(['--help'])


def run(arguments: typing.List[str] = None):
    """
    Executes a sloth_cli-cli command action

    :param arguments:
        The command line arguments to parse as a list. If omitted the standard
        sys.argv arguments will be used instead.
    """

    args = parsing.parse(arguments)
    default_action = 'version' if args.pop('version') else None
    if args.get('action'):
        action = args.pop('action') or default_action
    else:
        action = 'speed'

    actions = dict(
        version=show_version,
        speed=profiler.run
    )
    command = actions.get(action) or show_help
    command(**args)
