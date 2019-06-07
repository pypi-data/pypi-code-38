import re
import asyncio
import logging

import tornado.ioloop
import tornado.web
import tornado.httpclient
import tornado.netutil
import tornado.autoreload
from tornado.options import options, define
from tornado.escape import json_decode, json_encode
import tornado.platform.caresresolver
from tort.logger import configure_logging, tort_log
from jsonpointer import resolve_pointer, set_pointer

from .handler import PageHandler
from .processor import processors


define('debug', default=True, type=bool, help='Work in debug mode')
define('port', default=7777, type=int, help='Port to run on')
define('host', default='127.0.0.1', help='Host to run on')

define('dns_resolver', default='tornado.platform.caresresolver.CaresResolver', help='DNS resolver')

define('log_filename', default='/tmp/mockry.log', help='Log filename')
define('log_level', default=logging.DEBUG, help='Log level')

define('config', default=None, help='Path to configuration file')

define('json', default='application.json', help='Path to application file')


class StatusHandler(PageHandler):
    async def get(self):
        self.finish({
            'status': 'ok'
        })


class RouteHandler(PageHandler):
    def initialize(self, routes, **kwargs):
        PageHandler.initialize(self)

        self.matched_route = None
        self.routes = routes

        self.resolver = {
            'data': {},
            'request': {
                'body': self.request.body,
                'headers': self.request.headers
            }
        }

    def _match_route(self, match):
        for item in match:
            if item['type'] == 'path':
                if not re.match(item['path'], self.request.path):
                    self.log.debug('{} type not matched'.format(item['type']))
                    return False
            elif item['type'] == 'method':
                methods = [item['methods']] if not isinstance(item['methods'], list) else item['methods']
                if self.request.method.lower() not in list(map(lambda x: x.lower(), methods)):
                    self.log.debug('{} type not matched'.format(item['type']))
                    return False

        return True

    def _resolve_value(self, value, resolver=None):
        resolver = self.resolver if resolver is None else resolver

        value_type = value['type']
        if value_type == 'jsonpointer':
            return resolve_pointer(resolver, value['pointer'])
        elif value_type == 'dict':
            result = dict()
            for k, v in value['values'].items():
                result[k] = self._resolve_value(v, resolver)

            return result

        return value['value']

    def _set_value(self, pointer, value):
        set_pointer(self.resolver, pointer, value)

    def prepare(self):
        for route in self.routes:
            self.log.debug('Matching route named: {}'.format(route['name']))
            matched = self._match_route(route['match'])

            if matched:
                self.matched_route = route
                self.log.info('Matched route: {}'.format(route['name']))
                return

        raise tornado.web.HTTPError(404, 'No route matched')

    async def handle_request(self):
        for action in self.matched_route['actions']:
            if action['type'] == 'response':
                if action.get('code'):
                    self.set_status(action['code'])

                if action.get('output'):
                    self.finish(self._resolve_value(action['output']))
            elif action['type'] == 'sleep':
                self.log.info('Sleep for {} seconds'.format(action['seconds']))
                await asyncio.sleep(action['seconds'])
            elif action['type'] == 'request':
                request = action['request']
                request['method'] = request.get('method', 'GET').upper()

                if 'json' in request:
                    json = request.pop('json')
                    request['data'] = json_encode(self._resolve_value(json))
                    request['headers'] = request.get('headers', {})
                    request['headers']['Content-Type'] = 'application/json'

                req = self.make_request(action['name'], validate_cert=False, **request)
                response, = await self.fetch_requests([req])
                self.log.info(response.response.body)
            elif action['type'] == 'process':
                if action['processor'] not in processors:
                    self.log.error('No such processor: {}'.format(action['processor']))
                    continue

                processor = processors[action['processor']]
                result = processor(self._resolve_value(action['input']), options=action.get('options'))
                if action.get('name'):
                    self._set_value('/data/{}'.format(action['name']), result)
            elif action['type'] == 'combine':
                input = self._resolve_value(action['input']) if 'input' in action else self.resolver
                self._set_value('/data/{}'.format(action['name']), self._resolve_value(action['output'], input))

    async def get(self, *args, **kwargs):
        await self.handle_request()

    async def post(self, *args, **kwargs):
        await self.handle_request()


class Application(tornado.web.Application):
    def __init__(self, config):
        handlers = [
            (r'/status', StatusHandler),
            (r'.*', RouteHandler, config),
        ]

        settings = dict(
            debug=options.debug
        )

        tornado.web.Application.__init__(self, handlers, **settings)


def make_app(config):
    configure_logging(options.log_filename, options.log_level)

    tornado.httpclient.AsyncHTTPClient.configure('tornado.simple_httpclient.SimpleAsyncHTTPClient', max_clients=50)
    tornado.netutil.Resolver.configure(options.dns_resolver)

    return Application(config)


def main():
    tornado.options.parse_command_line()
    if options.config:
        tornado.options.parse_config_file(options.config)
        tornado.options.parse_command_line()

    with open(options.json, 'r') as f:
        config = json_decode(f.read())

    if options.debug:
        tornado.autoreload.watch(options.json)

    app = make_app(config)
    app.listen(options.port, options.host)

    tort_log.info('Starting server {}:{}'.format(options.host, options.port))

    tornado.ioloop.IOLoop.current().start()
