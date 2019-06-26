#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main module for tcmpr application used to run program
and parse arguments.
"""

import os
import sys
import logging
from .argument_parser import parse_args


__author__ = "Konrad Poreba"
__copyright__ = "Konrad Poreba"
__license__ = "mit"

_logger = logging.getLogger(__name__)


def compress(file_name, algorithm):
    """Pick proper algorithm chosen by the user
       and compress input file
    """
    if algorithm == 'huffman':
        from tcmpr.algorithms.huffman.compressor import compress_huffman
        compress_huffman(file_name)
    elif algorithm == 'lzss':
        from tcmpr.algorithms.lzss.compressor import compress_lzss
        compress_lzss(file_name)
    elif algorithm == 'lzw':
        from tcmpr.algorithms.lzw.compressor import compress_lzw
        compress_lzw(file_name)
    elif algorithm == 'shannon':
        pass
    else:
        _logger.error("No such algorithm implemented!")
        sys.exit()


def decompress(file_name):
    """Pick proper algorithm to decompress file
       based on coding extension attached to
       compressed file like:
         .huffman
         .lzw
         .lzss
         .shannon
    """
    coding_extension = os.path.splitext(os.path.basename(file_name))[1]
    if coding_extension == '.huffman':
        from tcmpr.algorithms.huffman.decompressor import decompress_huffman
        decompress_huffman(file_name)
    elif coding_extension == '.lzss':
        pass
    elif coding_extension == '.lzw':
        from tcmpr.algorithms.lzw.decompressor import decompress_lzw
        decompress_lzw(file_name)
    elif coding_extension == '.shannon':
        pass
    else:
        _logger.error("Unsupported file format!")
        sys.exit()


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=loglevel, stream=sys.stdout,
                        format=logformat, datefmt="%Y-%m-%d %H:%M:%S")


def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """
    args = parse_args(args)
    setup_logging(args.loglevel)

    if args.mode == 'compress':
        _logger.debug("Compression started")
        compress(args.file, args.algorithm)
        _logger.info("Compression complete")

    if args.mode == 'decompress':
        _logger.debug("Decompression started")
        decompress(args.file)
        _logger.info("Decompression complete")


def run():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
