###############################################################################
#
#   Copyright 2018-2019 Telefónica
#
#   Quickmock is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################


import argparse
import json
import logging
import os
import sys

from flask import Flask
from flask import Response
from flask import request

import quickmock
import quickmock.server as server
import quickmock.templating as templating
from quickmock.validation import ConfigurationReader
from quickmock.utils.exceptions import CorruptConfigurationFormatException



def main():
    """Main method to deal with mocked services

    Args:
        conf_files (list): List of paths from where the configuration files will
            be grabbed. All the information will be added to a single conf file.
    """

    def get_parser():
        """Method that gets a valid parser

        Returns:
            argparse.ArgumentParser.
        """
        parser = argparse.ArgumentParser(
            description="Quickmock | A tool for deploying quick HTTP server mocks",
            add_help=False
        )

        about_parser = parser.add_argument_group(
            'Other commands',
            'Get additional information about this program.'
        )
        about_parser.add_argument(
            '-h', '--help',
            action='help',
            help='shows this help and exits.'
        )
        about_parser.add_argument(
            '--version',
            action='version',
            version='%(prog)s ' + quickmock.__version__,
            help='shows the version of this package and exits.'
        )

        # Add subparsers
        # --------------
        subparsers = parser.add_subparsers(
            description='Available commands.',
            dest='subcommand',
            required=True,
            metavar="<SUBCOMMAND>"
        )

        # Server parser
        # ------------------
        server_subparser = subparsers.add_parser(
            'run',
            help='Run a mocked server.',
            conflict_handler='resolve'
        )

        server_main_subparser = server_subparser.add_argument_group(
            'Start the FLASK interfaces for the mock',
            "Deploy the services passed as parameters."
        )
        server_main_subparser.add_argument(
            '-c', '--configuration-files',
            metavar='<FILE_PATH>',
            nargs='+',
            action='store',
            required=True,
            help="Setting the configuration files for the Quickmock server."
        )
        server_main_subparser.add_argument(
            '-l', '--logging-level',
            metavar='<LOG_LEVEL>',
            action='store',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            default="INFO",
            help="Set the logging level."
        )

        # Subparser for template creation
        # -------------------------------
        template_subparser = subparsers.add_parser(
            'template',
            help='Create a template for a mocked service.',
            conflict_handler='resolve'
        )

        template_main_subparser = template_subparser.add_argument_group(
            'Template creation interface',
            "An interative interface for creating mocked services."
        )
        template_main_subparser.add_argument(
            '-t', '--template-file',
            metavar='<TEMPLATE_FILE>',
            default="./quickmock-template.json",
            help="the path to the template file. Default output file: ./quickmock-template.json"
        )
        template_main_subparser.add_argument(
            '-o', '--output-only',
            action="store_true",
            default=False,
            help="whether to print only the output. Default: False."
        )
        return parser

    parser = get_parser()

    args = parser.parse_args()

    if args.subcommand == "run":
        server.run(args)
    elif args.subcommand == "template":
        templating.create_template(args)


if __name__ == '__main__':
    main()
