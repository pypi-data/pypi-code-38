#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Общие методы создания и наполнение участков
"""
import traceback
import sys
import pkg_resources
version = pkg_resources.require('tracuni')[0].version

from aiozipkin.span import Span
import aiozipkin as az

from typing import (
    TYPE_CHECKING,
)

from tracuni.define.type import (
    SpanSide,
    UNKNOWN_NAME,
    Stage,
)
import tracuni.define.errors as err
from tracuni.misc.helper import json_dumps_decode, log_tracer_error
from tracuni.point.span_stages import ProvideSpanForStage
from tracuni.schema.lib.debug import debug_output
from tracuni.misc.select_coroutine import get_coroutine_decorator
from tracuni.schema.pipe_methods import pipe_mask_secret_catch_essentials

async_decorator = get_coroutine_decorator()

if TYPE_CHECKING:
    from tracuni.point.accessor import PointAccessor


class SpanGeneral:
    """Общая функциональность передачи данных на трассер

        * Реализует логику создания разных вариантов участков:
            * Входящий / Исходящий
            * С родительским контекстом / Без него
        * Записывает подготовленные данные в участок
            * В наименование
            * В заголовок
            * В аннотации

    """
    def __init__(self, side: SpanSide, point: 'PointAccessor'):
        self.span_instance = None
        self.side = side
        self.point = point
        self.tracer: az.Tracer = point.context.adapter.tracer
        self.error = None
        self.error_code = None
        self.has_been_started = False

###############################################################################
# Создание участков для каждого из двух направлений
# Задействуются декоратором ProvideSpanForStage

    def fab_in_span(self):
        # если в перехватываемых данных есть загловки трасера,
        # создаем дочерний входящий участок,
        # иначе создаем корневой входящий участок
        headers = self.point.context.reuse.get("tracer_headers", {})
        context = az.make_context(headers or {})
        span_instance: Span = (
            self.tracer.new_trace()
            if context is None else
            self.tracer.new_child(context)
        )
        if not span_instance.context.sampled:
            return
        span_instance.kind(az.SERVER)
        # сохраняем идентификаторы входящего участка
        # все исходящие участки в данном дереве асинхронных вызовов
        # будут использовать его в качестве родительского контекста
        self.point.context.adapter.keep_context.set(
            'span',
            span_instance.context.make_headers(),
        )
        self.point.context.adapter.keep_context.set(
            'span_name',
            'UNNAMED',
        )
        return span_instance

    def fab_out_span(self):
        # если в контексте нет входящего участка,
        # то исходящая точка вызывается вне сценария трассровки,
        # возвращаемся в перехватчик и делаем прямой вызов без трассировки
        in_span_context = self.point.context.adapter.keep_context.get('span')
        if in_span_context is None:
            raise err.SpanNoParentException
        # исходящий участок всегда создаётся как дочерний к входящему
        in_span_context = az.make_context(in_span_context)
        span_instance = self.tracer.new_child(in_span_context)
        span_instance.kind(az.CLIENT)

        return span_instance

    def enrich_headers(self, headers: dict, prefix_key=None):
        tracer_headers = self.span_instance.context.make_headers()
        if prefix_key:
            tracer_headers = {
                prefix_key: tracer_headers
            }
        headers.update(tracer_headers)
        return headers

###############################################################################
# Методы прохождения по этапу

    @ProvideSpanForStage(Stage.INIT)
    @async_decorator
    def run_init_stage(self, span: Span):
        span.start()
        self._load()
        self.has_been_started = True

    @ProvideSpanForStage(Stage.PRE)
    @async_decorator
    def run_pre_stage(self, _: Span):
        if not self.has_been_started:
            raise err.SpanIsNotStartedException
        self._load()

        self.point.apply_point()

    @ProvideSpanForStage(Stage.POST)
    @async_decorator
    def run_post_stage(self, span: Span):
        if not self.has_been_started:
            raise err.SpanIsNotStartedException
        self._load()
        error = None
        if self.error:
            error = self.error.get("error_message", self.error)
        span.finish(exception=error)
        if self.side == SpanSide.IN:
            self.point.context.adapter.keep_context.set('span', None)


    @async_decorator
    def run_stage(self, stage: Stage):
        stage_method_name = ProvideSpanForStage.stage_to_method.get(stage)
        stage_method = getattr(self, stage_method_name or "", None)
        if stage_method:
            yield from stage_method()

    @async_decorator
    def register_error(self, error: dict, error_code=200):
        self.error = error or 'unspecified error'
        self.error_code = error_code or 200

    def emergency_exit(self, exc):
        if self.span_instance and self.span_instance._record._timestamp:
            if self.error:
                self.span_instance.annotate(self.error['error_info'])
                self.span_instance.tag('error.class', self.error['error_class'])
                self.span_instance.tag('error.own', True)
            self.span_instance.finish(exception=self.error['error_message'])
            if self.side == SpanSide.IN:
                self.point.context.adapter.keep_context.set('span', None)

    ###############################################################################
# Area privata

    def _load(self):
        span = self.span_instance
        context = self.point.context
        span_name = context.span_name
        span_tags = context.span_tags
        span_logs = context.span_logs
        debug_info = context.debug
        error = self.error

        span.name(span_name.get('name', UNKNOWN_NAME))
        if self.side == SpanSide.IN:
            self.point.context.adapter.keep_context.set(
                'span_name',
                span_name.get('name', UNKNOWN_NAME),
            )
        custom_remote = context.reuse['custom_remote_endpoint_name']
        standard_remote = span_name.get('remote_endpoint', UNKNOWN_NAME)
        remote = (
            custom_remote.format(**{'standard': standard_remote})
            if custom_remote else
            standard_remote
        )
        span.remote_endpoint(remote)

        if span_logs is None:
            span_logs = []
        if span_tags is None:
            span_tags = {}

        for log_item in span_logs:
            if log_item and log_item != '{}':
                self.span_instance.annotate(log_item)
        self.point.update_context({"span_logs": []})
        for tag_name, tag_value in span_tags.items():
            if tag_name in ('data.url_in', 'data.url_out') and tag_value == 'null':
                tag_value = None
            if tag_value:
                if 'url' in tag_name:
                    tag_value = pipe_mask_secret_catch_essentials(tag_value)[0]
                self.span_instance.tag(tag_name, f"{tag_value}")
                if tag_name in ('data.payment_id', 'data.pid'):
                    self.span_instance.tag('pid', json_dumps_decode(tag_value))

        if self.span_instance._record._kind == az.SERVER:
            self.span_instance.tag('app.tracuni.version', version)

        if error:
            self.span_instance.annotate(error['error_info'])
            self.span_instance.tag('error.class', error['error_class'])

        if self.error_code:
            self.span_instance.tag('rsp.status', self.error_code)


        if debug_info:
            output = debug_output(context, debug_info)
            if output:
                self.span_instance.annotate(output)
            self.point.update_context({'debug': None})
