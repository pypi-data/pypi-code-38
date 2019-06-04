#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Pacifica Archive Interface.

Any new Backends added need to have the type argument extended
to support the new Backend Archie type

"""
from os import path, environ
from time import sleep
from threading import Thread
from argparse import ArgumentParser, SUPPRESS
import cherrypy
from .rest_generator import ArchiveInterfaceGenerator, error_page_default
from .backends.factory import ArchiveBackendFactory
from .globals import CONFIG_FILE, CHERRYPY_CONFIG


def stop_later(doit=False):
    """Used for unit testing stop after 60 seconds."""
    if not doit:  # pragma: no cover
        return

    def sleep_then_exit():
        """
        Sleep for 20 seconds then call cherrypy exit.

        Hopefully this is long enough for the end-to-end tests to finish
        """
        sleep(20)
        cherrypy.engine.exit()
    sleep_thread = Thread(target=sleep_then_exit)
    sleep_thread.daemon = True
    sleep_thread.start()


def main():
    """Main method to start the wsgi ref server."""
    parser = ArgumentParser(description='Run the archive interface.')

    parser.add_argument('--cherrypy-config', metavar='CP_CONFIG', type=str,
                        default=CHERRYPY_CONFIG, dest='cp_config',
                        help='cherrypy config file')
    parser.add_argument('-c', '--config', metavar='CONFIG', type=str,
                        default=CONFIG_FILE, dest='config',
                        help='archiveinterface config file')
    parser.add_argument('-p', '--port', metavar='PORT', type=int,
                        default=8080, dest='port',
                        help='port to listen on')
    parser.add_argument('-a', '--address', metavar='ADDRESS',
                        default='localhost', dest='address',
                        help='address to listen on')
    parser.add_argument('-t', '--type', dest='type', default='posix',
                        choices=['hpss', 'posix', 'hsmsideband'],
                        help='use the typed backend')
    parser.add_argument('--prefix', metavar='PREFIX', dest='prefix',
                        default='{}tmp'.format(path.sep), help='prefix to save data at')
    parser.add_argument('--stop-after-a-moment', help=SUPPRESS,
                        default=False, dest='stop_later',
                        action='store_true')

    args = parser.parse_args()

    # Get the specified Backend Archive
    factory = ArchiveBackendFactory()
    backend = factory.get_backend_archive(args.type, args.prefix)
    stop_later(args.stop_later)
    cherrypy.config.update({'error_page.default': error_page_default})
    cherrypy.config.update({
        'server.socket_host': args.address,
        'server.socket_port': args.port
    })
    cherrypy.quickstart(
        ArchiveInterfaceGenerator(backend),
        '/',
        args.cp_config
    )


def cmd(argv=None):
    """Command line admin tool for managing ingest."""
    parser = ArgumentParser(description='Admin command line tool.')
    parser.add_argument(
        '-c', '--config', metavar='CONFIG', type=str, default=CONFIG_FILE,
        dest='config', help='archiveinterface config file'
    )
    parser.add_argument(
        '-t', '--type', dest='type', default='posix',
        choices=['hpss', 'posix', 'hsmsideband'], help='use the typed backend'
    )
    parser.add_argument(
        '--prefix', metavar='PREFIX', dest='prefix',
        default='{}tmp'.format(path.sep), help='prefix to save data at'
    )
    subparsers = parser.add_subparsers(help='sub-command help')
    delete_parser = subparsers.add_parser(
        'delete', help='delete help', description='delete files')
    delete_parser.add_argument(
        'FILES', nargs='+',
        help='delete the files'
    )
    delete_parser.set_defaults(func=delete_file)
    args = parser.parse_args(argv)
    return args.func(args)


def delete_file(args):
    """Delete a file in the archive."""
    environ['ARCHIVEINTERFACE_CONFIG'] = args.config
    factory = ArchiveBackendFactory()
    backend = factory.get_backend_archive(args.type, args.prefix)
    for archfile in args.FILES:
        backend.open(archfile, 'r')
        backend.remove()
    return 0


if __name__ == '__main__':
    main()
