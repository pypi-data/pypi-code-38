# -*- tab-width: 4; encoding: utf-8; -*-
# ex: set tabstop=4 expandtab:
# Copyright (c) 2016-2018 by Lars Klitzke, Lars.Klitzke@hs-emden-leer.de.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import argparse
import logging
import os
import sys

from aiohttp import web
from pymodconf import parser

from osmserver import CONFIG_MAPPING, CONFIG_SECTION_OSMSERVER, CONFIG_SECTION_OSMSERVER_OPTION_HOST, \
    CONFIG_SECTION_OSMSERVER_OPTION_PORT
from osmserver.handler import handle_server_query_request, handle_ws_request

APP = None


def parse_arguments():
    """ Parses the arguments the user passed to this script """

    arg_parser = argparse.ArgumentParser(description="osmserver is a server to enable the execution of "
                                                     "overpass queries in parallel.")

    arg_parser.add_argument('--config', help="The program configuration file", required=False)

    arg_parser.add_argument('--log-level', help="""
        Defines which messages should be logged (INFO, DEBUG, WARNING, ERROR).
        For further modes see the logging class.""", default='INFO', choices=['INFO', 'DEBUG', 'WARNING', 'ERROR'])

    return arg_parser.parse_args()


def init():
    """
    Initialize the server

    Returns:
        tuple[str, int]: The host and port of the server.
    """
    # parse the program arguments
    arguments = parse_arguments()

    if not arguments.config:
        config_file = os.path.join(sys.prefix, 'share', 'osmserver.cfg')
    else:
        config_file = arguments.config

    config = parser.load(config_file, CONFIG_MAPPING)

    context = {
        'config': config_file,
        **config[CONFIG_SECTION_OSMSERVER]
    }

    global APP
    # setup the application
    APP = web.Application()

    # add the root routes
    APP.router.add_routes([
        web.get('/', lambda request: handle_server_query_request(request, **context)),
        web.post('/', lambda request: handle_server_query_request(request, **context)),
        web.get('/ws', lambda request: handle_ws_request(request, **context))]
    )

    logging.basicConfig(level=arguments.log_level)

    return config[CONFIG_SECTION_OSMSERVER].get(CONFIG_SECTION_OSMSERVER_OPTION_HOST, '127.0.0.1'), int(
        config[CONFIG_SECTION_OSMSERVER].get(CONFIG_SECTION_OSMSERVER_OPTION_PORT, '61111'))


def run(host='127.0.0.1', port=61111):
    """
    Run the server on `host` using `port`.+

    Args:
        host (str): Host to run on.
        port (int): Port to run on.
    """
    # run the application
    web.run_app(APP, host=host, port=port)


def main():
    """
    Run osmserver
    """
    host, port = init()

    run(host, port)


if __name__ == "__main__":
    main()
