"""CLI for rofetta.

"""


import os
import argparse
from rofetta import convert
from rofetta import __version__


def parse_args(args:iter=None) -> dict:
    return cli_parser().parse_args(args)


def cli_parser() -> argparse.ArgumentParser:
    """Return the dict of options set by CLI"""

    # main parser
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', '-v', action='version',
                        version="%(prog)s " + __version__)


    parser.add_argument('infile', type=existant_file,
                        help='file containing the input data')
    parser.add_argument('outfile', type=writable_file,
                        help='output file. Will be overwritted')

    return parser


def existant_file(filepath:str) -> str:
    """Argparse type, raising an error if given file does not exists"""
    if not os.path.exists(filepath):
        raise argparse.ArgumentTypeError("file {} doesn't exists".format(filepath))
    return filepath


def writable_file(filepath:str) -> str:
    """Argparse type, raising an error if given file is not writable.
    Will delete the file !

    """
    try:
        with open(filepath, 'w') as fd:
            pass
        os.remove(filepath)
        return filepath
    except (PermissionError, IOError):
        raise argparse.ArgumentTypeError("file {} is not writable.".format(filepath))


if __name__ == "__main__":
    args = parse_args()
    # print(args)
    convert(args.infile, args.outfile)
