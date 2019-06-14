#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Узел подключения к другим компонентам
        * обеспечивает взаимодействие с главным компонентом клиентского
        приложения и инициализируется вмете с ним;
        * хранит ссылку на главный компонент клиентского приложения;
        * получает, обрабатывает и сохраняет настройки журналирования;
        * создаёт драйверы подключения к внешним ресурсам журналирования;
        * выбирает варианты реализации асинхронности (для работы с aiohttp
         и для работы с Tornado);
        * уведомляет остальные компоненты библиотеки о своей готовности;

        .side_steps.stat.intercept.TracerTransport
            параллельная запись метрик
        .misc.helper.async_decorator,
            для подключения к Tornado
                    .HTTPServer,
                    .IOLoop,
                    .tornado_available,
        .misc.keep_tornado.context_accessor,
            сохранение родительского участка, используя механизм Tornado
"""
import logging
from abc import abstractmethod
from functools import partial

tornado_available = False
context_accessor = None

from tracuni.misc.select_coroutine import (
    get_coroutine_decorator,
    switch_to_tornado,
    HTTPServer,
    IOLoop,
)
# use only if tornado lib is available
if HTTPServer:
    from .misc.keep_tornado import context_accessor
    tornado_available = bool(switch_to_tornado())

from tracuni.adapter import (
    fab_tracer,
    FutureTracer,
)
import tracuni.define.errors as err

async_decorator = get_coroutine_decorator()


def init_tornado_loop(cls, port, app_conf, start_loop=False):
    # if HTTPServer:
    #     global context_accessor
    #     from .misc.keep_tornado import context_accessor
    #     tornado_available = bool(switch_to_tornado())
    if not tornado_available:
        raise err.TornadoNotAvailable

    logging_conf = app_conf.get('logging_conf')
    IOLoop.configure('tornado.platform.asyncio.AsyncIOLoop')
    this_app = cls(**app_conf)

    logging.info('%s listens at: %s' % (cls.__name__, port))

    tracer = fab_tracer(
        tracer_base_type=TracerBase
    )(
        this_app,
        logging_conf,
        app_conf.get('statsd_conf'),
        app_conf.get('system_conf'),
    )

    if tracer.config.enable:
        @async_decorator
        def prehook(request):
            context_accessor.run_root_with_context(
                coro=partial(this_app, request)
            )

        HTTPServer(prehook).listen(port)
    else:
        HTTPServer(this_app).listen(port)

    tracer.run()
    if start_loop:
        IOLoop.current().start()

    return


class TracerBase(FutureTracer):
    variant = 'tornado'

    def __init__(self):
        self.client = None
        super().__init__()
        self.log_info = None
        self.log_debug = None
        self.loop = IOLoop.current().asyncio_loop
        self.keep_context = context_accessor

    def run(self):
        self.log_info = getattr(
            self.client, 'log_info', logging.info
        )
        self.log_debug = getattr(
            self.client, 'log_debug', logging.debug
        )
        self.prepare_tracer()
        self.start_tracer()

    @abstractmethod
    def prepare_tracer(self):
        pass

    @abstractmethod
    def start_tracer(self):
        pass
