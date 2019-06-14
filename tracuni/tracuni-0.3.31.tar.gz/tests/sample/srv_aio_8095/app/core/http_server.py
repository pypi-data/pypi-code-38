import asyncio
from functools import partial

import aiohttp_jinja2
import jinja2
from aiohttp import web, web_runner, helpers
import traceback

from app.core.handler import BaseHandler
from app.core.helper import annotate_bytes
from .app import Component
import logging

access_logger = logging.getLogger('aiohttp.access')
SPAN_KEY = 'zipkin_span'

from tracuni import (
    tracer_point,
    Variant,
    SpanSide,
    APIKind,
)


class HttpServer(Component):
    def __init__(
            self,
            app,
            host,
            port,
            handler,
            shutdown_timeout=60.0,
            skip_trace=None,
            jinja_templates=None
    ):
        if not issubclass(handler, BaseHandler):
            raise UserWarning()
        super(HttpServer, self).__init__()
        self.app = app
        self.loop = app.loop
        self.web_app = web.Application(loop=self.loop, middlewares=[self.wrap_middleware, ])
        if jinja_templates:
            aiohttp_jinja2.setup(self.web_app, loader=jinja2.FileSystemLoader(jinja_templates))
        self.host = host
        self.port = port
        self.error_handler = None
        self.web_app_handler = None
        self.shutdown_timeout = shutdown_timeout
        self.uris = None
        self.handler = handler(self)
        self._sites: list = []
        self._runner: web_runner.AppRunner = None
        self.skip_trace = skip_trace or []

    async def wrap_middleware(self, app, handler):
        async def middleware_handler(request):
            if self.app.tracer:
                if request.path not in self.skip_trace:
                    context = az.make_context(request.headers)
                    if context is None:
                        sampled = azah.parse_sampled(request.headers)
                        debug = azah.parse_debug(request.headers)
                        span = self.app.tracer.new_trace(sampled=sampled, debug=debug)
                    else:
                        span = self.app.tracer.join_span(context)
                    request[SPAN_KEY] = span

                    with span:
                        span_name = '{0} {1}'.format(request.method.upper(), request.path)
                        span.name(span_name)
                        span.kind(azah.SERVER)
                        span.tag(HTTP_PATH, request.path)
                        span.tag(HTTP_METHOD, request.method.upper())
                        annotate_bytes(span, await request.read())
                        resp, trace_str = await self._handle(span, request, handler)
                        if trace_str is not None:
                            annotate_bytes(span, trace_str)
                        else:
                            if isinstance(resp, web.Response):
                                span.tag(azah.HTTP_STATUS_CODE, resp.status)
                                annotate_bytes(span, resp.body)
                        return resp
                else:
                    resp, trace_str = await self._handle(None, request, handler)
                    return resp
            else:
                resp, trace_str = await self._handle(None, request, handler)
                return resp

        return middleware_handler

    @tracer_point(Variant(SpanSide.IN, APIKind.HTTP), endpoint_name="custom")
    async def _handle(self, span, request, handler):
        try:
            resp = await handler(request)
            return resp, None
        except Exception as herr:
            trace = traceback.format_exc()

            if span:
                span.tag('error', 'true')
                span.tag('error.message', str(herr))
                span.annotate(trace)

            if self.error_handler:
                try:
                    resp = await self.error_handler(span, request, herr)
                except Exception as eerr:
                    if isinstance(eerr, web.HTTPException):
                        resp = eerr
                    else:
                        self.app.log_err(eerr)
                        resp = web.Response(status=500, text='')
                    trace = traceback.format_exc()
                    if span:
                        span.annotate(trace)
            else:
                if isinstance(herr, web.HTTPException):
                    resp = herr
                else:
                    resp = web.Response(status=500, text='')

            return resp, trace

    def add_route(self, method, uri, handler):
        if not asyncio.iscoroutinefunction(handler):
            raise UserWarning('handler must be coroutine function')
        self.web_app.router.add_route(method, uri, partial(self._handle_request, handler))

    def add_static(self, prefix, uri):
        self.web_app.router.add_static(prefix, uri)

    def set_error_handler(self, handler):
        if not asyncio.iscoroutinefunction(handler):
            raise UserWarning('handler must be coroutine function')
        self.error_handler = handler

    @staticmethod
    async def _handle_request(handler, request):
        res = await handler(request.get(SPAN_KEY), request)
        return res

    async def prepare(self):
        self.app.log_info("Preparing to start http server")
        self._runner = web_runner.AppRunner(
            self.web_app,
            handle_signals=True
        )

        await self._runner.setup()

        self._sites = []
        self._sites.append(web_runner.TCPSite(
            self._runner,
            self.host,
            self.port,
            shutdown_timeout=self.shutdown_timeout,
            ssl_context=None,
            backlog=128))

    async def start(self):
        self.app.log_info("Starting http server")
        await asyncio.gather(*[site.start() for site in self._sites], loop=self.loop)
        self.app.log_info('HTTP server ready to handle connections on %s:%s' % (self.host, self.port))

    async def stop(self):
        self.app.log_info("Stopping http server")
        if self._runner:
            await self._runner.cleanup()
