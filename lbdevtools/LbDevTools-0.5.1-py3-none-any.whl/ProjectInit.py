#!/usr/bin/env python
###############################################################################
# (c) Copyright 2018 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
Script to initialize a project for the build.
'''
__author__ = 'Marco Clemencic <marco.clemencic@cern.ch>'


def main():
    import os
    import logging

    from argparse import ArgumentParser
    from LbDevTools import initProject
    from LbDevTools.GitTools.common import (add_verbosity_argument,
                                            handle_verbosity_argument,
                                            add_version_argument)

    parser = ArgumentParser(description='Initialize a directory for building '
                            'a project (e.g. from a plain git clone). If the '
                            'argument project_root_dir is not specified, the '
                            'required files are created in the current '
                            'directory.')

    add_version_argument(parser)

    parser.add_argument('path', nargs='?',
                        metavar='project_root_dir')

    parser.add_argument('--overwrite', action='store_true',
                        help='overwrite existing files [default: %default]')

    add_verbosity_argument(parser)

    parser.set_defaults(path=os.curdir,
                        overwrite=False)

    args = parser.parse_args()
    handle_verbosity_argument(args)

    logging.debug("using project root '%s'", args.path)

    initProject(args.path, args.overwrite)
