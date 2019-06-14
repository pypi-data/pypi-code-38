#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Узел подключения к другим компонентам
        * обеспечивает взаимодействие с главным компонентом клиентского приложения и инициализируется вмете с ним;
        * хранит ссылку на главный компонент клиентского приложения;
        * получает обрабатывает и сохраняет настройки журналирования;
        * создаёт драйверы подключения к внешним ресурсам журналирования;
        * выбирает варианты реализации асинхронности (для работы с aiohttp и для работы с Tornado);
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
import re
from abc import (
    ABC,
    abstractmethod,
)
import logging
from typing import (
    Union,
    Type,
)

import aiozipkin as az
import aiozipkin.transport as azt

from tracuni.define.type import (
    TracerOptions,
    StatsdOptions,
    StatsdOptionsMeasureNames)
from tracuni.define.const import (
    TRACER_SYSTEM_NAME,
)
import tracuni.side_steps.stat.send
import tracuni.define.errors as err

try:
    import aiotask_context
except ImportError:
    aiotask_context = None


class TracerObserve:
    """Временный класс подключаемый до полной инициализации адаптера

        Пока при запуске приложения ещё не создан полноценный класс делаем
        заглушку, которая позволяет другим объектам подписываться на
        изменения состояния трассера и получить уведомление о том,
        что к работе всё готово
    """
    observers = []
    open_span_points = {}

    @classmethod
    def register_state_observer(cls, observer):
        """Подписаться на уведомления о переходе в состоние готовности
        This

        Parameters
        observer
            экземпляр клиента с соответвующим методом, получающим уведомление
        """
        fn = getattr(observer, 'observe_state_change')
        if callable(fn):
            cls.observers.append(observer)


class FutureTracer(ABC):
    tracer = None
    custom_schema = None
    config = None
    should_not_trace = None
    client = None


AdapterType = Type[Union[TracerObserve, FutureTracer]]
TracerAdapter = TracerObserve  # type: AdapterType


def fab_tracer(component_class=None, tracer_base_type=None):
    # обертка драйвера сервиса метрик
    from tracuni.side_steps.stat.send import (
        TracerTransport as StatsTracerTransport,
    )
    if tracer_base_type is None:
        class TracerBase(component_class, FutureTracer):
            variant = 'core'

            def __init__(self):
                super().__init__()
                self.log_info = None
                self.log_debug = None
                self.loop = getattr(self.client, 'loop', None)
                self.loop.set_task_factory(
                    aiotask_context.copying_task_factory
                )
                self.keep_context = aiotask_context

            async def prepare(self):
                self.log_info = getattr(
                    self.client, 'log_info', logging.info
                )
                self.log_debug = getattr(
                    self.client, 'log_debug', logging.debug
                )
                self.prepare_tracer()

            async def start(self):
                self.start_tracer()

            async def stop(self):
                await self.stop_tracer()

            async def stop_tracer(self):
                if self.tracer:
                    self.log_info("Shutting down tracer")
                    await self.tracer.close()
                    self.tracer = None
                    self._notify_observers()

            @abstractmethod
            def prepare_tracer(self):
                pass

            @abstractmethod
            def start_tracer(self):
                pass
        tracer_base_type = TracerBase

    class TracerWrapper(tracer_base_type, TracerObserve):
        instance = None

        def __init__(self,
                     client,
                     config_logging,
                     config_statsd,
                     config_system=None,
                     custom_schema=None,
                     ):
            """

            Parameters
            ----------
            client
                ссылка на основной объект приложения клиента
            config_logging
                конфигурация трассера
            config_statsd
                конфигурация сервиса метрик
            config_system
                общая системная конфигуация, используется для получения
                строк имен сервис по адресам для именования исходящих участкоа
            custom_schema
                схема заменяющая или дополняющая стандартную схему бибилиотеки
            """
            self.client = client
            super().__init__()
            self.tracer = None
            self.custom_tracer_transport = None
            self.custom_schema = custom_schema

            # устанавливаем настройки по умолчанию, потом пишем их поверх из
            # файла
            self.config: TracerOptions = TracerOptions()
            self.config = self._compose_options(config_logging, config_statsd)
            self.url_service_map = self._create_url_service_map(config_system)
            self.custom_tracer_transport = tracuni.side_steps.stat.send.TracerTransport(
                self.config,
                self.config.statsd,
                loop=self.loop,
                use_tornado=self.variant == 'tornado'
            )

            skip_list_src = self.config.skip_trace
            self.skip_list = [
                re.compile(r'^{}$'.format(el))
                for el in skip_list_src
            ]

        def prepare_tracer(self):
            if TracerWrapper.instance is not None:
                return
            if not self.config.enable:
                return
            endpoint = az.create_endpoint(self.config.service_name)
            sampler = az.Sampler(sample_rate=self.config.sample_rate)

            transport = self.custom_tracer_transport
            if transport is None:
                transport = azt.Transport(
                    self.config.url,
                    send_interval=self.config.send_interval,
                    loop=self.loop
                )

            self.tracer = az.Tracer(transport, sampler, endpoint)

        def start_tracer(self):
            if self.tracer is not None:
                TracerWrapper.instance = self
                self._notify_observers()
                self.log_info('Tracer started to: {}'.format(
                    self.config.url))

        def should_not_trace(self, path):
            return any(el.match(path) for el in self.skip_list)

        def _notify_observers(self):
            for ob in self.observers:
                fn = getattr(ob, 'observe_state_change')
                if callable(fn):
                    fn(self)

        def _compose_options(self,
                             cfg_trace_log,
                             cfg_time_log
                             ) -> TracerOptions:
            # Включаем трассер,если имя в конфиге пристуствует и
            # соответствует заданному и если имя в конфиге или в значениях
            # по умолчанию не установлено в false
            tracer_name = cfg_trace_log.get('tracer', 'zipkin')
            unexpected_name = tracer_name != TRACER_SYSTEM_NAME
            disabled_by_default = self.config.enable
            disabled_in_config = cfg_trace_log.get(
                'enable',
                cfg_trace_log.get('tracer_enable', disabled_by_default)
            ) is False
            tracer_enable = not (unexpected_name or disabled_in_config)

            # Получаем именнованный кортеж опций трассера с вложенным
            # кортежом опций statsd и сохранеными значениями по умолчанию у
            # того и другого, поскольку значения,
            # отсутствующие в файле конфигурации пропускаем
            measure_names_cfg = cfg_time_log.get('measure_names', {})
            measure_names = dict((k, v) for k, v in (
                ('check_count', measure_names_cfg.get('check_count')),
                ('db_time', measure_names_cfg.get('db_time')),
                ('http_in_code_count', measure_names_cfg.get('http_in_code_count')),
                ('http_in_method_time', measure_names_cfg.get('http_in_method_time')),
                ('http_out_time', measure_names_cfg.get('http_out_time')),
                ('exception_count', measure_names_cfg.get('exception_count')),
            ) if v is not None)
            read_statsd_opts = dict((k, v) for k, v in (
                ('enable', cfg_time_log.get('enable')),
                ('logging', cfg_time_log.get('logging')),
                ('url', cfg_time_log.get('url')),
                ('prefix', cfg_time_log.get('prefix')),
                ('hb_interval', cfg_time_log.get('hb_interval')),
                ('measure_names', StatsdOptionsMeasureNames(**measure_names)),
            ) if v is not None)
            read_tracer_opts = dict((k, v) for k, v in (
                ('name', tracer_name),
                ('enable', tracer_enable),
                ('service_name', cfg_trace_log.get('service_name', cfg_trace_log.get('tracer_svc_name'))),
                ('url', cfg_trace_log.get('url', cfg_trace_log.get('tracer_url'))),
                ('sample_rate', cfg_trace_log.get('sample_rate', cfg_trace_log.get('tracer_sample_rate'))),
                ('send_interval', cfg_trace_log.get('send_interval', cfg_trace_log.get('tracer_send_interval'))),
                ('skip_trace', cfg_trace_log.get('skip', cfg_trace_log.get('skip_trace'))),
                ('debug', cfg_trace_log.get('debug', False)),
                ('statsd', StatsdOptions(**read_statsd_opts)),
                ('context_amqp_name', cfg_trace_log.get('context_amqp_name')),
            ) if v is not None)
            return TracerOptions(**read_tracer_opts)

        @staticmethod
        def _create_url_service_map(system_conf):
            if system_conf is None:
                return {}
            return dict(
                (v, k)
                for k, v in system_conf.items()
                if isinstance(v, str)
            )

    global TracerAdapter
    TracerAdapter = TracerWrapper

    return TracerWrapper
