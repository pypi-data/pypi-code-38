#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Модуль доступа к вызываемой точке

"""
import logging
import traceback
import re
from collections import namedtuple
from copy import copy
from functools import partial
from inspect import signature, Parameter
from typing import (
    NamedTuple,
    Callable,
    Sequence,
    Dict,
    Any,
    MutableSequence,
)

from tracuni.point.span_general import SpanGeneral
from tracuni.misc.helper import compose_own_call_stack
from tracuni.define.const import (
    PATH_IGNORE_METHODS,
    PATH_IGNORE_PIECE,
    COLLECT_TRACE,
)
from tracuni.define.type import (
    PointContext,
    Stage,
    Destination,
    Variant,
    SpanSide,
    APIKind,
)
import tracuni.define.errors as err
from tracuni.schema.pipe_methods import pipe_mask_secret_catch_essentials
from tracuni.misc.select_coroutine import get_coroutine_decorator, ASYNC_VARIANT
async_decorator = get_coroutine_decorator()


class PointAccessor:
    """Доступ к точке вызова и связанным с ней данным

    * Хранит контекст: ссылки на точку, аргументы, сокращённый стек вызовов
    и схему варианта точки
    * Преобразует все аргументы к именованным, основываясь на сигнатуре
    точки и переданным именованным аргументам для упрощения доступа к ним
    * Копирует записываемое в трассер содержимое аргументов перед их
    модификацией
    * Регистрирует сигнал о достижении определённой фазы, вызывает извлечение
    данных этой фазы по схеме варианта
    * Хранит извлеченные данные в определённой структуре, предназначенной
    для записи в трассер и для переиспользования на последующих шагах работы
    экстрактора
    * Модифицирует ограниченное множество аргументов (заголовки HTTP)
    * Вызывает точку с оригинальными и модифицированными аргументами
    """

    def __init__(self,
                 original_args: Sequence,
                 original_kwargs: Dict,
                 point_context: PointContext):
        self._positional_names = []
        self._original_args = original_args
        self._original_kwargs = original_kwargs
        self._applied_point = None
        self._done = False
        self.pass_itself_as_kwargs_item = False

        point_args = self._compose_kwargs(point_context.point_ref)

        # noinspection PyProtectedMember
        self.context = PointContext(**{
            **point_context._asdict(),
            "point_args": point_args,
        })
        self._span_general = SpanGeneral(
            self.context.engine.schema_feed.variant.span_side,
            self,
        )
        if not self._span_general:
            raise err.NoSpanException

    @classmethod
    def fab_default(cls, args, kwargs, point_coro, schema_engine, remote_name):
        return cls(
            args,
            kwargs,
            PointContext(
                point_ref=point_coro,
                engine=schema_engine,
                adapter=schema_engine.adapter,
                client=schema_engine.adapter.client,
                reuse={
                    "custom_remote_endpoint_name": remote_name,
                    "error": None,
                    "should_not_trace": False,
                },
                debug={},
                headers={},
                span_name={},
                span_tags={},
                span_logs=[],
            ),
        )

    def stack_frames_to_context(self, current_frame):
        point_coro = self.context.point_ref
        stack_frames = (
            # первым элементом - название вызываемого метода
            {
                'full_path': point_coro.__qualname__,
                'short_path': point_coro.__name__,
            },
        )
        if COLLECT_TRACE:
            # собрать данные по стэку вызовов в данной точке
            # inspect.getouterframes(inspect.currentframe())

            frame_list = []
            frame = current_frame
            while frame:
                frame_list.append(frame)
                frame = frame.f_back
            stack_frames = (
                # добавить название вызываемого метода
                *stack_frames,
                *compose_own_call_stack(
                    PATH_IGNORE_METHODS,  # пропустить методы с именами
                    PATH_IGNORE_PIECE,  # пропустить модули по такому пути
                    result_length=5,  # общий размер списка не превышает
                    from_index=1,  # начинать просмотр стэка с позиции
                    look_up_stop_idx=10,  # не просматривать дальше позиции
                    frame_list=frame_list,  # стэк
                )
            )
        # noinspection PyProtectedMember
        self.context = PointContext(**{
            **self.context._asdict(),
            "call_stack": stack_frames,
        })

    def apply_point(self):
        kwargs = copy(self._original_kwargs)
        # noinspection PyProtectedMember
        kwargs.update(self.context.point_args._asdict())
        kwargs.pop('method_arguments_without_names')
        args = list(self._original_args)
        for idx, pos_name in enumerate(
            self._positional_names[:len(self._original_args)]
        ):
            args[idx] = kwargs.pop(pos_name, None)

        if self.pass_itself_as_kwargs_item:
            kwargs['tracuni_point'] = self

        self._applied_point = partial(self.context.point_ref, *args, **kwargs)

    @async_decorator
    def run(self):
        result = None
        if self.context.span and self._applied_point:
            try:
                variant = self.context.engine.schema_feed.variant
                if (
                    ASYNC_VARIANT == "TORNADO"
                    and
                    variant == Variant(SpanSide.OUT, APIKind.INNER_RETRY)
                ):
                    span_context = self.context.adapter.keep_context
                    result = yield from span_context.run_root_with_context(coro=self._applied_point)
                else:
                    result = yield from self._applied_point()
            finally:
                self._done = True
            self.update_context({"point_result": result})
        return result

    def has_not_been_done(self):
        return not self._done

    @async_decorator
    def register_stage(self, stage: Stage):
        yield from self._span_general.run_stage(stage)

    @async_decorator
    def register_error(self, exc, exc_info):
        found_exc_name = re.search(r"<class '(.*)'>", str(type(exc))).groups()
        if found_exc_name:
            found_exc_name = found_exc_name[0].split('.')[-1]
        else:
            found_exc_name = ''
        error = {
            "error_class": found_exc_name,
            "error_message": pipe_mask_secret_catch_essentials(str(exc))[0],
            "error_info": pipe_mask_secret_catch_essentials(
                '\n'.join(traceback.format_exception(*exc_info)),
            )[0],
        }
        self._span_general.register_error(error, getattr(exc, 'error_code', None))
        return error

    def register_own_error(self, exc):
        if isinstance(
            exc,
            (err.HTTPPathSkip, err.SpanNoParentException)
        ):
            return True
        else:
            self._span_general.emergency_exit(exc)

    def update_context(self, new_data):
        # noinspection PyProtectedMember
        self.context = PointContext(**{
            **self.context._asdict(),
            **new_data,
        })

    def update_context_by_destination(
        self,
        destination: Destination,
        val: Any,
    ):
        """

        Parameters
        ----------
        destination
            Данные по назначению записи
        val
            Значение которое надо отправить в контекст
        """

        # noinspection PyProtectedMember
        dest = self.context._asdict().get(
            destination.section.name.lower()
        )
        if dest is None:
            return

        elif isinstance(dest, MutableSequence):
            dest.append(val)

        elif isinstance(dest, dict):
            if isinstance(destination.name, dict):
                dest.update(val)
            else:
                dest[destination.name] = val

        elif "PointArguments" in str(type(dest)):
            # noinspection PyProtectedMember
            old_vals = dest._asdict()
            new_args = namedtuple("PointArguments", old_vals)(**{
                **old_vals,
                destination.name: {
                    **(old_vals.get(
                        destination.name,
                        {}
                    ) or {}),
                    **val,
                }
            })
            self.update_context({"point_args": new_args})

        else:
            try:
                if destination.name:
                    setattr(dest, destination.name, val)
            except AttributeError:
                raise err.ProcessorExtractCantSetDestinationAttr

    def _compose_kwargs(self, point_ref: Callable) -> NamedTuple:
        sig = signature(point_ref).parameters
        self._positional_names = arg_names = [
            el
            for el in sig
            if el not in ('args', 'kwargs')
        ]
        kwargs = copy(self._original_kwargs)
        args = copy(self._original_args)
        kwargs.update(zip(arg_names, args))

        param_desc = sig
        for param in param_desc:
            pass_value = kwargs.get(param, param_desc.get(param).default)
            if pass_value != Parameter.empty:
                kwargs[param] = pass_value

        kwargs_l = len(kwargs)
        kwargs.update({'method_arguments_without_names': None})
        if kwargs_l < len(args):
            kwargs['method_arguments_without_names'] = args[kwargs_l:]

        point_args = namedtuple(
            'PointArguments',
            kwargs
        )(**kwargs)

        return point_args
