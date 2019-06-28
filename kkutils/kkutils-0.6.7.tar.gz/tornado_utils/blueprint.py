#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tornado Blueprint蓝图的实现。"""
import asyncio
import collections
import logging
import signal
import types

import six
import tornado.netutil
import tornado.process
import tornado.web
import uvloop
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define
from tornado.options import options
from utils import get_ip

__all__ = ['Blueprint', 'BlueprintMeta', 'Application']


class BlueprintMeta(type):
    derived_class = []

    def __new__(cls, name, bases, attr):
        _class = super(BlueprintMeta, cls).__new__(cls, name, bases, attr)
        cls.derived_class.append(_class)
        return _class

    @classmethod
    def register(cls, app):
        for _class in cls.derived_class:
            for blueprint in _class.blueprints:
                app.register(blueprint)


@six.add_metaclass(BlueprintMeta)
class Blueprint(object):
    blueprints = []

    def __init__(self, name=None, url_prefix='/', host='.*', strict_slashes=False):
        assert url_prefix[0] == '/'
        self.name = name
        self.host = host
        self.url_prefix = url_prefix.rstrip('/')
        self.rules = []
        self.blueprints.append(self)
        self.strict_slashes = strict_slashes

    def route(self, uri, params=None, name=None):
        def decorator(Handler):
            assert uri[0] == '/'
            rule_name = name or Handler.__name__
            if self.name:
                rule_name = f'{self.name}.{rule_name}'
            rule_uri = self.url_prefix + uri
            self.rules.append((rule_uri, Handler, params, rule_name))
            if not self.strict_slashes and rule_uri.endswith('/'):
                self.rules.append((rule_uri.rstrip('/'), Handler, params, None))
            return Handler
        return decorator


class Application(Blueprint):

    def __init__(self, name=None, url_prefix='/', host='.*', strict_slashes=False, **kwargs):
        super().__init__(name, url_prefix, host, strict_slashes)
        self.logger = logging
        self.kwargs = kwargs
        self.handlers = []
        self.disabled_handlers = []
        self.cache_enabled = False
        self.events = collections.defaultdict(list)
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

        define("debug", default=True, help="debug mode", type=bool)
        define("port", default=8000, help="listen port", type=int)
        define("workers", default=1, help="running workers", type=int)
        options.parse_command_line()

    def listen(self, event):
        def decorater(func):
            self.events[event].append(func)
        return decorater

    def register(self, *blueprints, url_prefix='/'):
        assert url_prefix[0] == '/'
        url_prefix = url_prefix.rstrip('/')
        for blueprint in blueprints:
            rules = [(url_prefix + x[0], *x[1:]) for x in blueprint.rules]
            for rule in rules:
                setattr(rule[1], 'app', self)
            self.handlers.append((blueprint.host, rules))

    def url_for(self, endpoint, *args, **kwargs):
        return self.app.reverse_url(endpoint, *args, **kwargs)

    def make_app(self, **kwargs):
        kwargs.setdefault('static_path', 'static')
        kwargs.setdefault('template_path', 'templates')
        kwargs.setdefault('cookie_secret', 'YWpzYWhkaDgyMTgzYWpzZGphc2RhbDEwMjBkYWph')
        kwargs.setdefault('xsrf_cookie', True)
        kwargs.setdefault('login_url', '/signin')
        kwargs.setdefault('gzip', True)
        kwargs.setdefault('debug', options.debug)
        app = tornado.web.Application(**kwargs)
        app.logger = logging
        app.cache_enabled = False
        app.options = options
        for host, rules in self.handlers:
            rules = [x for x in rules if x[0] not in self.disabled_handlers]
            app.add_handlers(host, rules)
        return app

    async def shutdown(self):
        for func in self.events['before_server_stop']:
            ret = func(self)
            if isinstance(ret, types.CoroutineType):
                await ret

        self.server.stop()
        self.logger.info('shutting down')
        tasks = [task for task in asyncio.Task.all_tasks() if task is not
                 asyncio.tasks.Task.current_task()]
        if tasks:
            self.logger.warning(f'canceling {len(tasks)} pending tasks')
            await asyncio.sleep(1)
            task = asyncio.gather(*tasks, return_exceptions=True)
            task.cancel()

        self.loop.stop()

    def sig_handler(self, sig, frame):
        self.logger.warning(f'received signal {sig}')
        self.loop.add_callback_from_signal(self.shutdown)

    def run(self, port=None, workers=None, xheaders=True, max_buffer_size=None):
        port = port or options.port
        workers = workers or options.workers
        sockets = tornado.netutil.bind_sockets(port)
        if not options.debug and workers > 1:
            tornado.process.fork_processes(workers)

        self.register(self)
        self.app = self.make_app(**self.kwargs)
        self.loop = IOLoop.current()

        for func in self.events['before_server_start']:
            ret = func(self)
            if isinstance(ret, types.CoroutineType):
                self.loop.asyncio_loop.run_until_complete(ret)

        self.server = HTTPServer(self.app, xheaders=xheaders, max_buffer_size=max_buffer_size)
        self.server.add_sockets(sockets)
        signal.signal(signal.SIGTERM, self.sig_handler)
        signal.signal(signal.SIGINT, self.sig_handler)
        self.logger.info(f"Debug: {self.app.settings['debug']}, Running: http://{get_ip()}:{port}")
        self.loop.start()
