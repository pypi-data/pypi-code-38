#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Metadata Module."""
import os
from time import sleep
from threading import Thread
from argparse import ArgumentParser, SUPPRESS
import cherrypy
from pacifica.metadata.rest.root import Root, error_page_default
from pacifica.metadata.orm.sync import OrmSync
from pacifica.metadata.globals import CHERRYPY_CONFIG, CONFIG_FILE


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
    parser = ArgumentParser(description='Run the metadata server.')
    parser.add_argument('--cpconfig', metavar='CPCONFIG', type=str,
                        default=CHERRYPY_CONFIG, dest='cpconfig',
                        help='cherrypy config file')
    parser.add_argument('-c', '--config', metavar='CONFIG', type=str,
                        default=CONFIG_FILE, dest='config',
                        help='database config file')
    parser.add_argument('-p', '--port', metavar='PORT', type=int,
                        default=8121, dest='port',
                        help='port to listen on')
    parser.add_argument('-a', '--address', metavar='ADDRESS',
                        default='localhost', dest='address',
                        help='address to listen on')
    parser.add_argument('--stop-after-a-moment', help=SUPPRESS,
                        default=False, dest='stop_later',
                        action='store_true')
    args = parser.parse_args()
    os.environ['METADATA_CONFIG'] = args.config
    OrmSync.connect_and_check()
    stop_later(args.stop_later)
    cherrypy.config.update({'error_page.default': error_page_default})
    cherrypy.config.update({
        'server.socket_host': args.address,
        'server.socket_port': args.port
    })
    cherrypy.quickstart(Root(), '/', args.cpconfig)


if __name__ == '__main__':
    main()
