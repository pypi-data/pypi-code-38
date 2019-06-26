import argparse
import logging
import sys
import os
from tcmpr import __version__


def create_parser():
    """Function that create parser, helpful in writing
       test cases
    """
    parser = argparse.ArgumentParser(
        description="tcmpr program to compress or decompress text data")
    parser.add_argument(
        '-c',
        '--compress',
        dest='mode',
        action='store_const',
        help='set if you want to compress file',
        const='compress',
    )

    parser.add_argument(
        '-d',
        '--decompress',
        dest='mode',
        action='store_const',
        help='set if you want to decompress file',
        const='decompress'
    )

    parser.add_argument(
        '-alg',
        '--algorithm',
        choices=['huffman', 'lzss', 'lzw', 'shannon'],
        dest='algorithm',
        help='choose algorithm which you would like to use in compression'
    )

    parser.add_argument(
        '-r',
        '--recursive',
        dest='recursive_mode',
        action='store_true',
        default=False
    )

    parser.add_argument(
        dest="file",
        help="Name of file which you would like to compress/decompress",
        type=str,
        metavar="filename")

    parser.add_argument(
        '--version',
        action='version',
        version='tcmpr {ver}'.format(ver=__version__))

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

    parser.set_defaults(mode='compress')
    parser.set_defaults(algorithm='huffman')
    return parser


def parse_args(args):
    """Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = create_parser()
    arguments = parser.parse_args(args)
    if not os.path.isfile(os.path.abspath(arguments.file)):
        if os.path.isdir(os.path.abspath(arguments.file)) and not arguments.recursive_mode:
            logging.error("Directory passed instead of file!\n"
                          "If you would like to pass directory, use flag -r or --recursive")
            sys.exit()
    return parser.parse_args(args)
