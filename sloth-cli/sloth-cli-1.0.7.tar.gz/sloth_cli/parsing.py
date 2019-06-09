import argparse
import typing
from argparse import ArgumentParser


def parse(arguments: typing.List[str] = None):
    """
    Parses the command line arguments for current execution

    :param arguments:
        The command line arguments to parse as a list. If omitted the standard
        sys.argv arguments will be used instead.
    """
    parser = ArgumentParser()
    parser.add_argument('--version', action='store_true', default=False)
    subparsers = parser.add_subparsers(dest='action')

    speed = subparsers.add_parser(
        'speed', description='Shows seconds spent per line'
    )
    speed.add_argument(
        '--file-name', '-f',
        help='The file name to analyse',
        dest='filename'
    )
    speed.add_argument(
        '--lines', '-l',
        help='The number of lines to print',
        default=100
    )
    speed.add_argument(
        '--sort', '-s',
        help='How to sort the values: time, cumulative, calls, and filename. '
             'Defaults to cumulative',
        default='cumulative'
    )

    args_docs = """
    args or kwargs to be passed to the script being called:
    If the script you are running takes any args or kwargs you can pass them to 
    the script by using the "--cmd" argument. Do that by adding: --cmd {kwargs}. 
    E.g.:
        sloth-cli speed -f tester.py --cmd fake --fake-arg test
            or
        sloth-cli speed -f tester.py -l 100 --cmd --help
        
    This will run the following: tester.py fake --fake-arg test
    """
    speed.add_argument(
        '--cmd',
        help=args_docs,
        nargs=argparse.REMAINDER
    )

    return vars(parser.parse_args(args=arguments))
