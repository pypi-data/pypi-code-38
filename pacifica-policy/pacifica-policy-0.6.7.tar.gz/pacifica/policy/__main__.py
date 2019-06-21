#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This is the policy module.

This module is organized by workflow type used by each subproject
of the overall Pacifica software... So there's an uploader module
under which are queries that you can apply policy to to change the
behavour of the uploader.
"""
from __future__ import print_function, absolute_import
from time import sleep
from threading import Thread
from argparse import ArgumentParser, SUPPRESS
import cherrypy
from pacifica.policy.root import Root, error_page_default
from pacifica.policy.globals import CHERRYPY_CONFIG


def stop_later(doit=False):
    """Used for unit testing stop after 10 seconds."""
    if not doit:  # pragma: no cover
        return

    def sleep_then_exit():
        """sleep for 10 seconds then call cherrypy exit."""
        sleep(10)
        cherrypy.engine.exit()
    sleep_thread = Thread(target=sleep_then_exit)
    sleep_thread.daemon = True
    sleep_thread.start()


def main():
    """Main method to start the httpd server."""
    parser = ArgumentParser(description='Run the policy server.')
    parser.add_argument(
        '-c', '--config', metavar='CONFIG', type=str, default=CHERRYPY_CONFIG,
        dest='config', help='cherrypy config file'
    )
    parser.add_argument(
        '-p', '--port', metavar='PORT', type=int, default=8181,
        dest='port', help='port to listen on'
    )
    parser.add_argument(
        '-a', '--address', metavar='ADDRESS', default='localhost',
        dest='address', help='address to listen on'
    )
    parser.add_argument(
        '--stop-after-a-moment', help=SUPPRESS, default=False,
        dest='stop_later', action='store_true'
    )
    args = parser.parse_args()
    stop_later(args.stop_later)
    cherrypy.config.update({'error_page.default': error_page_default})
    cherrypy.config.update({
        'server.socket_host': args.address,
        'server.socket_port': args.port
    })
    cherrypy.quickstart(Root(), '/', args.config)
