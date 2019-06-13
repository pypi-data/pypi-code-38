#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Перехват вызова интересующей точки
    Во время перехвата запускается процесс сбора, обработки и записи данных,
    согласно связаным с перехватчиком набором правил
"""
import inspect
import logging
from functools import wraps
import sys

from tracuni.adapter import TracerAdapter
from tracuni.schema.engine.engine import SchemaEngine
from tracuni.define.type import (
    Variant,
    RuleSet,
    Stage,
    Part,
)
from tracuni.misc.helper import (
    PostgreSQLError,
    log_tracer_error,
)
from tracuni.point.accessor import PointAccessor
from tracuni.misc.select_coroutine import get_coroutine_decorator
async_decorator = get_coroutine_decorator()


def tracer_point(
    variant: Variant,
    remote_name: str = None,
    point_ruleset: RuleSet = None,
    part: Part = None,
    reraise_exceptions: bool = False,
):
    """

    Parameters
    ----------
    reraise_exceptions
    variant
        Назначить вариант обработки точки
    remote_name
        Здесь можно передать пользовательское имя удаленной точки
        при этом можно использовать и стандартное, указав в строке место
        подстановки с именем standard: 'mine: {standard}'
    point_ruleset
        Здесь можно передать свой вариант настройки извлечения формат такой
        же как значение одного из ключей стандартной настройки она заменит
        стандартную настройку конкретного варианта для данной точки,
        если же последним элементом пользовательской настройки будет строка
        '...', то пользовательская объединится со стандартной с приоритетом
        пользовательской в любом случае далее удут применены менее
        специфичные и менее приоритетные настройки, относящиеся к данной точке
    part
        разрывает обработку на две части, закрытие участка происходит во второй

    Returns
    -------
        Декорированный метод, вызов которого будет трассироваться

    """
    # создание экземпляра обработчика
    schema_engine = SchemaEngine(variant, point_ruleset)
    # подписываемся, чтобы знать состояние трассера
    TracerAdapter.register_state_observer(schema_engine)

    def wrapper(point_coro):

        @wraps(point_coro)
        @async_decorator
        def decorated(*args, **kwargs):
            result = {}
            point = None
            debug_is_on = False

            if schema_engine.is_tracer_disabled():
                # сразу запускаем обернутую точку, если трассер выключен,
                # не соединился или не создан
                result = yield from point_coro(*args, **kwargs)
                return result

            if part in (Part.CLOSE, Part.CLOSE_AFTER):
                open_point = None
                open_span_id = None
                try:
                    if part == Part.CLOSE_AFTER:
                        result = yield from point_coro(*args, **kwargs)
                    open_span_context = schema_engine.adapter.keep_context.get('span')
                    if open_span_context:
                        open_span_id = open_span_context.get('X-B3-SpanId')
                        if open_span_id:
                            open_point = schema_engine.adapter.open_span_points.get(open_span_id)
                        yield from open_point.register_stage(Stage.POST)
                except Exception as exc:
                    if open_point:
                        if open_span_id:
                            schema_engine.adapter.open_span_points.pop(open_span_id, None)
                        open_point.register_own_error(exc)
                finally:
                    if open_span_id:
                        schema_engine.adapter.open_span_points.pop(open_span_id, None)
                    if part == Part.CLOSE:
                        result = yield from point_coro(*args, **kwargs)
                    return result

            try:

                debug_is_on = schema_engine.adapter.config.debug

                point = PointAccessor.fab_default(
                    args,
                    kwargs,
                    point_coro,
                    schema_engine,
                    remote_name,
                )
                point.stack_frames_to_context(inspect.currentframe())

                # создаем спан сконфигрированный по варианту и связанный с
                # ним и точкой
                # this_span = point.fab_span_general()
                # если не создан участок переходим к прямому вызову
                yield from point.register_stage(Stage.INIT)

                if debug_is_on:
                    parent_span_context = schema_engine.adapter.keep_context.get('span')
                    logging.debug(schema_engine.schema_feed.variant)
                    logging.debug(f'Span context from task context: {parent_span_context}')

                if point.context.span:
                    yield from point.register_stage(Stage.PRE)

            except Exception as exc:
                # если здесь вылетели, то рабочий участок создать не удалось
                if point:
                    stop = point.register_own_error(exc)
                    if stop:
                        point = None
                log_tracer_error(exc, debug_is_on)

            finally:
                if point:
                    # в любом случае должны вызвать обернутую точку
                    if part == Part.OPEN and point and point.context and point.context.span:
                        open_span_id = point.context.span.span_instance.context.span_id
                        point.context.adapter.open_span_points[open_span_id] = point
                    try:
                        result = yield from point.run()
                    except (Exception, PostgreSQLError) as exc:
                        if point:
                            point.register_error(exc, sys.exc_info())
                        # фиксируем данные об исключении
                        if debug_is_on:
                            logging.exception(exc)
                        if reraise_exceptions:
                            raise exc

                    finally:
                        # так или иначе пробуем завершить формирование
                        # участка трассера
                        if part is None:
                            try:
                                yield from point.register_stage(Stage.POST)
                            except Exception as exc:
                                if point:
                                    point.register_error(exc, sys.exc_info())
                                    point.register_own_error(exc)
                                log_tracer_error(exc, debug_is_on)

                if not point or point.has_not_been_done():
                    # если вызов через аксессор не удался, вызываем напрямую
                    result = yield from point_coro(*args, **kwargs)

            return result

        return decorated

    return wrapper
