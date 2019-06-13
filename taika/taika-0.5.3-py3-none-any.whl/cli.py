# -*- coding: utf-8 -*-

"""
:mod:`taika.cli`
================

The entry point for the command line interface of Taika.
"""
import argparse
import os
import sys

from taika import Taika
from taika.taika import TAIKA_CONF


def parse_arguments(arguments):
    """Create a :class:`argparse.ArgumentParser` and run :meth:`argparse.ArgumentParser.parse_args`
    agains `arguments`.

    Parameters
    ----------
    arguments : list
        A list of arguments to be parsed.

    Returns
    -------
    namespace : `argparse.Namespace`
        The namespace created when `arguments` are parsed.
    """
    parser = argparse.ArgumentParser(prog="taika")
    parser.add_argument("source", help="The directory that contains the files to be parsed.")
    parser.add_argument("destination", help="The directory that will contain the parsed files.")
    parser.add_argument(
        "-c",
        "--conf",
        default=os.getenv("TAIKA_CONF"),
        help=f"The configuration file for Taika. Default to '{TAIKA_CONF}', but it can be "
        "setted using the environment variable 'TAIKA_CONF'.",
    )

    return parser.parse_args(arguments)


def main(arguments=None):
    """The main entry point, parse `arguments` behaves accordingly.

    Parameters
    ----------
    arguments : list, optional (default=None)
        A list of arguments to be parsed. If ``None``, ``sys.argv[1:]`` is used.

    Returns
    -------
    err_code : int
        Non-zero value indicates error, or zero on success.
    """
    if arguments is None:
        arguments = sys.argv[1:]

    args = parse_arguments(arguments)
    site = Taika(args.source, args.destination, args.conf)
    site.process()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
