#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Выбор декоратора асинхронных методов для превращения их в корутины

    По умлчанию используется декоратор из коробки types.coroutine.
    Он является ранней реализацией async|await и полностью совместим с этим
    механизмом

    Возможно глобальное переключение соответствующий декоратор из пакета
    Tornado

"""
import types

ASYNC_VARIANT = "ASYNCIO"
async_decorator = types.coroutine

try:
    # noinspection PyPackageRequirements
    from tornado.gen import coroutine as tornado_decorator
    # noinspection PyPackageRequirements
    from tornado.ioloop import IOLoop, PeriodicCallback
    # noinspection PyPackageRequirements
    from tornado.httpserver import HTTPServer
    # noinspection PyPackageRequirements
    from tornado.stack_context import run_with_stack_context, StackContext
except ImportError:
    tornado_decorator = None
    HTTPServer = None
    PeriodicCallback = None
    IOLoop = None
    run_with_stack_context = None
    StackContext = None


def switch_to_tornado():
    global async_decorator
    if tornado_decorator:
        async_decorator = tornado_decorator
    return tornado_decorator


def get_coroutine_decorator():
    if is_tornado_on():
        return tornado_decorator
    return async_decorator


def is_tornado_on():
    return ASYNC_VARIANT == "TORNADO"
