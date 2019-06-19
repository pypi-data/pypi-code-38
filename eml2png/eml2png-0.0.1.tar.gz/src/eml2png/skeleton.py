#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is a skeleton file that can serve as a starting point for a Python
console script. To run this script uncomment the following lines in the
[options.entry_points] section in setup.cfg:

    console_scripts =
        eml2png = eml2png.skeleton:run

Then run `python setup.py install` which will install the command `eml2png`
inside your current environment.
Besides console scripts, the header (i.e. until _logger...) of this file can
also be used as template for Python modules.
"""

import argparse
import logging
import os
import sys

from . import __version__, to_png

__author__ = "poipoii"
__copyright__ = "poipoii"
__license__ = "mit"

_logger = logging.getLogger(__name__)


def eml_to_png(input, output=None):
    """eml_to_png function

    Args:
      input (str): input EML file
      output (str): output PNG file (Default: None)

    Returns:
      str: output PNG file path. Return input + '.png' if output is None.
    """
    assert input is not None
    if not os.path.isfile(input):
        input = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            input
        )
    assert os.path.isfile(input) is True
    output = output if output else '{}.png'.format(input)
    open(output, 'wb').write(to_png(input))
    return output


def parse_args(args):  # pragma: no cover
    """Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(
        description="Just a Fibonnaci demonstration")
    parser.add_argument(
        '--version',
        action='version',
        version='eml2png {ver}'.format(ver=__version__))
    parser.add_argument(
        "--input",
        help="Input EML file",
        type=str)
    parser.add_argument(
        "--output",
        help="Output PNG file",
        type=str,
        action='store',
        default=None)
    parser.add_argument(
        '-v',
        '--verbose',
        dest="loglevel",
        help="set loglevel to INFO",
        action='store_const',
        const=logging.INFO)
    parser.add_argument(
        '-vv',
        '--very-verbose',
        dest="loglevel",
        help="set loglevel to DEBUG",
        action='store_const',
        const=logging.DEBUG)
    return parser.parse_args(args)


def setup_logging(loglevel):  # pragma: no cover
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=loglevel, stream=sys.stdout,
                        format=logformat, datefmt="%Y-%m-%d %H:%M:%S")


def main(args):  # pragma: no cover
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    print("eml_to_png: {}".format(eml_to_png(args.input, args.output)))


def run():  # pragma: no cover
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
