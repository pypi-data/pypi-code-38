from __future__ import (absolute_import, division, print_function, unicode_literals)

import logging

import click

from .klass_ws import WS


@click.command()
@click.option('--logfile', '-l',
              type=click.Path(file_okay=True, dir_okay=False, writable=True, readable=True, resolve_path=True,
                              allow_dash=True), required=False, help='Logfile path')
@click.option('--host', '-h', type=click.STRING, default='0.0.0.0',
              help='Interface on which launch the webservice, default=\'0.0.0.0\'')
@click.option('--port', '-p', type=click.INT, default=5000,
              help='Port on which the webservices is exposed, default=5000', )
@click.option('--token', '-t', type=click.STRING, default=None, help='Token for the security, default=None')
@click.option('--name', '-n', type=click.STRING, default=None, help='Name of the webservices')
@click.option('--debug', is_flag=True, default=False, help='Launch on debug mode')
def cli_ws_agent(logfile, host, port, token, name, debug):
    """Command line to launch the python console webservice"""
    ws_kwargs = {'debug': debug}
    if host: ws_kwargs['host'] = host
    if port: ws_kwargs['port'] = port
    if token: ws_kwargs['token'] = token
    if name: ws_kwargs['name'] = name
    ws = WS(**ws_kwargs)
    if logfile:
        logging.basicConfig(filename=logfile, level=logging.DEBUG)
    ws.start()
