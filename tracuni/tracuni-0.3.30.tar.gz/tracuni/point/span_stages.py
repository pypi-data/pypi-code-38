#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Обработка участков на каждом этапе
"""
import sys
from functools import wraps

from tracuni.define.type import (
    SpanSide,
    Stage,
)
import tracuni.define.errors as err
from tracuni.misc.select_coroutine import get_coroutine_decorator
from tracuni.misc.helper import log_tracer_error

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from aiozipkin.span import Span
    from typing import Dict
    from tracuni.define.type import MethodNameToStage
async_decorator = get_coroutine_decorator()


class ProvideSpanForStage:
    """Декоратор для методов этапа
            * Гарантирует наличие экземпляра участка
            * Получает наполнение для текущей стадии
            * Сохранят результат вызова точки

        Parameters
        ----------
        stage
            Привязывает декорированный метод к конкретному этапу. Если таких
            несколько, то привязывается только первый обработанный

        Returns
        -------
            Метод обработки определённого этапа
    """
    # Отношение наименований методов аксессора точки к запускаемым фазам
    # извлечения, отрабатывающим до выполнения этих методов.
    method_to_stage = {
        # 'run_init_stage': Stage.INIT,
        # 'run_pre_stage': Stage.PRE,
        # 'run_post_stage': Stage.POST,
    }  # type: MethodNameToStage

    stage_to_method = {}  # type: Dict[Stage, str]

    def __init__(self, stage: Stage):
        self.stage = stage
        self.span_general = None

    def __call__(self, fn):
        # Сохраняем прямое и обраное отображение этапов на методы обработки
        self.fn_name = fn_name = fn.__name__
        if fn_name and self.stage not in self.method_to_stage:
            self.method_to_stage[fn_name] = self.stage
            self.stage_to_method[self.stage] = fn_name

        @wraps(fn)
        @async_decorator
        def wrapper(span_general):
            try:
                self.span_general = span_general
                self.point = span_general.point

                # Получаем текущий этап
                stage_found = self._detect_stage()
                # Запускаем дополнительные операции для данного этапа
                self._stage_operations(stage_found)
                # Запускаем основной конвейер извлечения данных для участка
                yield from self._run_stage_pipe(stage_found)
                # Пропускаем данный участок и его детей, если это входящий HTTP, чей адрес указан в опции skip
                self._skip_http()
                # Создаём экземпляр участка, если его ещё нет
                span_instance = self._create_span_inst_if_none()

                # Запускаем метод формирования участка на данном этапе
                yield fn(span_general, span_instance)

            except Exception as exc:
                debug_is_on = self.point.context.adapter.config.debug
                log_tracer_error(exc, debug_is_on)
                if self.point:
                    self.point.register_error(exc, sys.exc_info())
                span_general.emergency_exit(exc)

            return

        return wrapper

###############################################################################
# Area privata
    def provide_span_and_point(fn):
        def wrapper(self, *args, **kwargs):
            span_general = self.span_general
            point = getattr(span_general, 'point', None)
            if not point:
                raise err.NoSpanException
            return fn(self, span_general, point, *args, **kwargs)
        return wrapper

    @provide_span_and_point
    def _stage_operations(self, span_general, point, stage_found):
        _ = span_general

        # Для этапа после вызова точки сохраняем результат её работы
        if stage_found == Stage.POST:
            result = None
            if (
                not result
                and
                hasattr(
                    point.context.point_args,
                    'self',
                )
                and
                hasattr(
                    point.context.point_args.self,
                    'response_body',
                )
            ):
                result = point.context.point_args.self.response_body
            if point.context.point_result is None:
                point.update_context({"point_result": result})

    @provide_span_and_point
    def _detect_stage(self, span_general, point):
        _ = span_general
        _ = point

        # Определяем текущий этап
        stage_found = self.method_to_stage.get(self.fn_name)
        if not stage_found:
            raise err.SpanNoStageForMethod

        return stage_found

    @provide_span_and_point
    def _skip_http(self, span_general, point):
        _ = span_general
        # обрабатываем выставленный обработчиками флаг пропуска
        if point.context.reuse.get('should_not_trace'):
            raise err.HTTPPathSkip

    @provide_span_and_point
    @async_decorator
    def _run_stage_pipe(self, span_general, point, stage_found):
        _ = span_general
        # Вызываем извлечение и обработку данных этапа
        pipe_fn = point.context.engine.extract

        point_context = yield from pipe_fn(point, stage_found)
        if point_context is None:
            point_context = point.context
        point.context = point_context

    @provide_span_and_point
    def _create_span_inst_if_none(self, span_general, point):
        # создаём участок, если он ещё не создан
        span_instance: Span = getattr(
            span_general,
            'span_instance',
            None
        )
        if span_instance is None:
            if span_general.side == SpanSide.IN:
                span_instance = span_general.fab_in_span()
            elif span_general.side in (SpanSide.OUT, SpanSide.MID,):
                span_instance = span_general.fab_out_span()

            if span_instance is None:
                raise err.NoSpanException
            span_general.span_instance = span_instance

        if not point.context.span:
            point.update_context({"span": span_general})

        return span_instance
