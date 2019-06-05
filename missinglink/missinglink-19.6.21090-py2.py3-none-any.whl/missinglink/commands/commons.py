# -*- coding: utf-8 -*-
import base64
import hashlib
import json
import logging
import os
import random
import socket
import sys
import types

import click
from missinglink.core.api import BASE_URL_PATH, ApiCaller
from requests import HTTPError
from terminaltables import PorcelainTable
from six.moves.urllib import parse

from .utilities.tables import format_json_data, dict_to_csv

NO_RESULTS_MESSAGE = "No results."


def _write_key_val(key_val, out_file):
    key, val = key_val
    json.dump(key, out_file)
    out_file.write(':')
    json.dump(val, out_file)


def _print_as_json_gen(result, out_file):
    markers = {True: '[]', False: '{}'}

    first_result = None
    is_list = True

    for item in result:
        if first_result is None:
            first_result = item
            is_list = len(first_result) == 1 or isinstance(first_result, dict)

            out_file.write(markers[is_list][0])
        else:
            out_file.write(',\n')

        if is_list:
            json.dump(item, out_file)
        else:
            _write_key_val(item, out_file)

    if first_result is None:
        out_file.write(markers[is_list][0])

    out_file.write(markers[is_list][1])


def print_as_json(result, out_file=None):
    out_file = out_file or sys.stdout

    if isinstance(result, types.GeneratorType):
        _print_as_json_gen(result, out_file)
    else:
        json.dump(result, out_file)


def add_to_data_if_not_none(data, val, key):
    if val is not None:
        data[key] = val


def get_data_and_remove(kwargs, key):
    key = key.lower()
    result = kwargs.get(key)

    if key in kwargs:
        del kwargs[key]

    return result


def base64url(b):
    return bytearray(base64.b64encode(b).decode('ascii').replace('=', '').replace('+', '-').replace('/', '_'), 'ascii')


def sha256(s):
    h = hashlib.sha256()
    h.update(s)
    return h.digest()


def urljoin(*args):
    base = args[0]
    for u in args[1:]:
        base = parse.urljoin(base, u)

    return base


class LocalWebServer(object):
    ports = [27017, 41589, 55130, 6617, 1566, 17404, 44288, 6948, 15950, 48216, 3318, 34449, 22082, 22845, 37862, 59304]

    def __init__(self):
        self.app = self.create_app()
        self.code = None
        self.srv = None

        self.disable_logging()
        self.start_server()

    def close(self):
        if self.srv is not None:
            self.srv.server_close()

    @classmethod
    def disable_logging(cls):
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

    def create_app(self):
        from flask import Flask, request, redirect
        app = Flask(__name__)

        @app.route('/console/auth/init')
        def auth_init():
            self.code = request.args.get('code')
            return redirect("/console/auth/finish")

        @app.route('/console/auth/finish')
        def auth_finish():
            self.srv.shutdown_signal = True
            return "User authenticated. Close this tab and go back to the console."

        return app

    def run(self):
        self.srv.serve_forever()

    @property
    def redirect_uri(self):
        return 'http://localhost:%s/console/auth/init' % self.srv.port

    def start_server(self):
        from werkzeug.serving import make_server

        ports = self.ports[:]
        random.shuffle(ports)

        for port in ports:
            try:
                self.srv = make_server('127.0.0.1', port, self.app)
                break
            except (OSError, socket.error):
                continue

        if self.srv is None:
            click.echo("can't create local server for authentication, consider using the --disable-webserver flag")


class WaitForHttpResponse:
    ports = [27017, 41589, 55130, 6617, 1566, 17404, 44288, 6948, 15950, 48216, 3318, 34449, 22082, 22845, 37862, 59304]

    def __init__(self, on_response=None, uri='/', methods=['GET'], port=None):
        self.uri = uri
        self.methods = methods
        self.on_response = on_response
        self.app = self.create_app()
        self.port = port
        self.response = None
        self.srv = None
        self.url = None
        self.disable_logging()
        self.start_server()

    def close(self):
        if self.srv is not None:
            self.srv.server_close()

    @classmethod
    def disable_logging(cls):
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

    def create_app(self):
        from flask import Flask, request
        app = Flask(__name__)

        @app.route(self.uri, methods=self.methods)
        def read_result():
            self.response = dict(request.args)
            result = None
            if self.on_response is not None:
                result = self.on_response(request)
            self.srv.shutdown_signal = True
            return result or 'ok'

        return app

    def run(self):
        self.srv.serve_forever()
        return self.response

    def start_server(self):
        from werkzeug.serving import make_server

        ports = self.ports[:] if self.port is None else [self.port]
        random.shuffle(ports)
        for port in ports:
            try:
                self.srv = make_server('127.0.0.1', port, self.app)
                self.url = 'http://127.0.0.1:%s%s' % (port, self.uri)
                break
            except (OSError, socket.error):
                continue

        if self.srv is None:
            click.echo("can't create local server for authentication, consider using the --disable-webserver flag")


def wait_for_input():
    if sys.version_info >= (3, 0):
        code = input('Enter the token ')
    else:
        # noinspection PyUnresolvedReferences
        code = raw_input('Enter the token ')

    return code


def ml_auth_oauth_token(api_host, session, code, verifier, redirect_uri):
    params = {
        'code': code,
        'code_verifier': verifier,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri,
    }

    url = '{}/{}users/token'.format(api_host, BASE_URL_PATH)
    r = session.post(url, json=params)

    r.raise_for_status()

    return r.json()


# noinspection PyUnusedLocal
def pixy_flow(ctx):
    import webbrowser

    verifier = base64url(os.urandom(32))
    verifier_challenge = base64url(sha256(verifier))
    verifier_challenge = verifier_challenge.decode('ascii')

    verifier = verifier.decode('ascii')

    def get_authorize_url():
        current_redirect_uri = app.redirect_uri if ctx.local_web_server else '{host}/console/auth/init'.format(host=ctx.host)

        query = {
            'redirect_uri': current_redirect_uri,
            'code_challenge': verifier_challenge,
        }

        return '{}/console/auth?{}'.format(ctx.host, parse.urlencode(query)), current_redirect_uri

    app = LocalWebServer() if ctx.local_web_server else None

    authorize_url, redirect_uri = get_authorize_url()

    if ctx.local_web_server and not webbrowser.open(authorize_url):
        app.close()
        ctx.local_web_server = False
        authorize_url, redirect_uri = get_authorize_url()

    if ctx.local_web_server:
        msg = "If the browser doesn't open enter this URL manually\n{authorize_url}\n"
    else:
        msg = "Enter the following URL in your machine browser\n{authorize_url}\n"

    click.echo(msg.format(authorize_url=authorize_url))

    if ctx.local_web_server:
        app.run()
        code = app.code
    else:
        code = wait_for_input()

    try:
        data = ml_auth_oauth_token(ctx.api_host, ctx.session, code, verifier, redirect_uri)
    except HTTPError:
        click.echo("Failed to init authorized (did you enter the correct token?).", err=True)
        sys.exit(1)

    click.echo("Success!, you are authorized to use the command line.")

    return data['access_token'], data['refresh_token'], data['id_token']


def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func

    return _add_options


def output_result(ctx, result, fields=None, formatters=None, write_row_index=False, progress=None):
    if result is None:
        return

    if getattr(ctx.obj, 'store_result'):
        ctx.obj.result = result
        return

    format_tables = ctx.obj.output_format == 'tables'
    format_csv = ctx.obj.output_format == 'csv'
    format_json_lines = ctx.obj.output_format == 'json-lines'

    result = format_json_data(result, formatters)

    def normal_name(name):
        return name.replace('_', ' ').title()

    if format_csv:
        from pandas.io.json import json_normalize

        df = json_normalize(list(result))
        df = df.rename(normal_name, axis='columns')

        df.to_csv(sys.stdout, columns=map(normal_name, list(df.columns)), index=write_row_index)
    elif format_tables:
        table_data = list(dict_to_csv(result, fields))
        click.echo(PorcelainTable(table_data).table)
        if len(table_data) <= 1:
            click.echo(NO_RESULTS_MESSAGE)

    elif format_json_lines:
        for item in result:
            print_as_json(item)
    else:
        print_as_json(result)


def is_empty_str(val):
    return val in (None, '')


def api_get(ctx, path):
    return ApiCaller.call(ctx.obj, ctx.obj.session, 'get', path)
