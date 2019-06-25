"""Find package installation candidates."""

import argparse
import logging as lg

from . import __version__


def build_parser():  # TODO: unit-test
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version="%(prog)s " + __version__
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="increase verbosity"
    )
    return parser


def setup_logging(verbose=0):  # TODO: unit-test
    level = lg.WARNING - lg.DEBUG * verbose
    format_ = "[%(levelname)8s] %(name)s: %(message)s"
    lg.basicConfig(level=level, format=format_)


def run_command(args):  # TODO: unit-test
    setup_logging(args.verbose)


def main():  # TODO: unit-test
    parser = build_parser()
    args = parser.parse_args()
    run_command(args)


if __name__ == "__main__":  # pragma: no cover
    main()
