# -*- coding: utf-8 -*-
"""cnx-db database control"""
from __future__ import print_function
import argparse

from .discovery import discover_subcommands


def create_main_parser():
    parser = argparse.ArgumentParser(__doc__)
    discover_subcommands(parser)
    return parser


def main(argv=None):
    parser = create_main_parser()
    args = parser.parse_args(argv)

    return args.cmd(args)


__all__ = ('main',)
