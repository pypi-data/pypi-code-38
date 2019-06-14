# -*- coding: utf-8 -*-

"""Интерфейс trac_uni."""


try:
    import config.tracuni_async_config
    async_variant = getattr(config.tracuni_async_config, "ASYNC_VARIANT", "ASYNCIO")
    suppress_bd_spans = getattr(config.tracuni_async_config, "SUPPRESS_BD_SPANS", False)
except ImportError:
    async_variant = "ASYNCIO"
    suppress_bd_spans = False
import tracuni.misc.select_coroutine as select_coroutine
select_coroutine.ASYNC_VARIANT = async_variant
import tracuni.schema.engine.engine as engine
engine.SUPPRESS_BD_SPANS = suppress_bd_spans

from .intercept import (
    tracer_point,
)
from .adapter import fab_tracer
from .adapter_tornado import init_tornado_loop
from .side_steps.db_logger.logger import Logger as DBLogger

from .define import errors

from .define.type import (
    Schema,
    Extractors,
    RuleSet,
    Rule,
    Origins,
    Origin,
    OriginSection,
    Destination,
    DestinationSection,
    Pipeline,
    PipelineTee,
    TeeDescriptor,
    PipeCommand,
    Stage,
    Variant,
    SpanSide,
    APIKind,
    Part,
)

__author__ = """Konstantin Gonciarou"""
__email__ = 'konstantin.goncharov@inplat.ru'
__version__ = '0.3.31'

__all__ = (
    # interceptor
    'fab_tracer',  # инициализация адаптера для работы с aiohttp приложением
    'init_tornado_loop',  # инициализация для работы с Tornado приложением
    'tracer_point',  # декоратор перехвата вызова точки и запуска извлечения
    # Types
    'Schema',  # Списки правил по всем вариантам
    'Extractors',  # Списки правил конкретного варианта по этапам
    'RuleSet',  # Список правил для обработки конкретной точки
    'Rule',  # Правило - откуда, куда. на каком этапе переместить данные и
             # как их обработать, либо команда управления применением правил
    'Stage',  # этап обработки одной точки
    'Origins',  # Список описаний источников данных
    'Origin',  # Описание одного источника данных
    'OriginSection',  # Разделы извлечения данных
    'Pipeline',  # Список методов последовательной обработки данных
    'PipeCommand',  # Обработчик-команда упрвления самим процессом обработки
    'PipelineTee',  # Разветвление потока данных при обработке
    'TeeDescriptor',  # Описание работы разветвления
    'Destination',  # Описание назначения обработанных данных
    'DestinationSection',  # Разделы, куда попадают обработанные данные
    'Variant',  # Вариант обработки
    'SpanSide',  # Сторона варианта
    'APIKind',  # Вид интерфейса варианта
    'Part',
    # auxiliary logging
    'DBLogger',
    'errors',
)

"""Структура модулей по смысловым блокам

 ☐ Сопряжение:
        adapter
        misc.keep_tornado
   ☐ Инициализация и конфигурация при старте приложения
   ☐ Выбор асинхронного механизма
   ☐ Сохранение родительского контекста участка

 ☐ Перехват:
        intercept
        point_accessor
   ☐
   ☐ Ссылки на данные

 ☐ Управление потоком:
        schema.engine ( cache | feed | engine )
        schema.standard
   ☐ Составление схем
   ☐ Проведение данных через обработку

 ☐ Фиксация:
        span
        side_steps ( db_logger | stat )
   ☐ Создание участков
   ☐ Наполнение участков
   ☐ Параллельная запись в другие сервисы

 ☐ Обработка:
        schema.builtin ( ext_* | pipe | helper )
   ☐ Подготовка данных для записи

 ☐ Вспомогательные:
        define ( type | const | errors )
        misc.helper
   ☐ Общие вспомогательные методы
   ☐ Структуры данных
   ☐ Внутренние настроечные данные
   ☐ Пользовательские исключения
"""
