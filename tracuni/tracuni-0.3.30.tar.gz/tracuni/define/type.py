#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Спецификация структур данных, используемых по всему коду библиотеки

Структура данных для извлечения
    * VariantToSchema Карта схем = Вариант - Схема
    * Variant Вариант = Направление + ВидИнтерфейса
    * Side Направление = К себе / От себя
    * APIKind ВидИнтерфейса = HTTP / ...(открытый список)
    * Schema Схема = список Правил
    * Rule Правило извлечения = Назначение + Источник + Фаза + Конвейер
    * Destination Назначение = РазделНазначения + имя метки
    * DestinationSection РазделНазначения = аннотации / метки заголовка ...
    * Origin Источник = РазделИсточника + функция / имя атрибута
    * OriginSection РазделИсточника = аргументы / результат / контейнер ...
    * Stage Фаза = Старт / До / После
    * Pipe Конвейер = список функций

"""

from enum import Enum
from functools import total_ordering

from typing import (
    NamedTuple,
    Iterable,
    Callable,
    Optional,
    Sequence,
    Dict,
    Union,
    Any,
    Tuple,
    Type,
)
from typing import TYPE_CHECKING

from .const import UNKNOWN_NAME

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from ..schema.engine.engine import (
        SchemaEngine,
    )  # pragma: no cover
    assert SchemaEngine  # pragma: no cover
    # noinspection PyUnresolvedReferences
    from ..adapter import TracerWrapper  # pragma: no cover
    # noinspection PyUnresolvedReferences
    from tracuni.point.span import SpanGeneral  # pragma: no cover


###############################################################################
# Вспомогательные типы


@total_ordering
class EnumAuto(Enum):
    """Добавить к старым версиям перечислений возможность автоматического
    присвоения индексных значений
    """

    def __new__(cls: Type['EnumAuto']) -> 'EnumAuto':
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __lt__(self, other: 'EnumAuto') -> Optional[bool]:
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


###############################################################################
# Структура конфигурации трассера и сервиса метрик и значения по умолчанию


StatsdOptionsMeasureNames = NamedTuple('StatsdOptionsMeasureNames', [
    ('check_count', Optional[str]),
    ('exception_count', Optional[str]),
    ('http_in_code_count', Optional[str]),
    ('http_in_method_time', Optional[str]),
    ('http_out_time', Optional[str]),
    ('db_time', Optional[str]),
])


StatsdOptionsMeasureNames.__new__.__defaults__ = (  # type: ignore
    'heartbeat', 'exception', 'gen_response_code', 'handler_timers', 'http_requests', 'db_query_function',
)


StatsdOptions = NamedTuple('StatsdOptions', [
    ('enable', bool),
    ('logging', bool),
    ('url', str),
    ('prefix', str),
    ('hb_interval', int),
    ('host', Optional[str]),
    ('port', Optional[int]),
    ('measure_names', Optional[StatsdOptionsMeasureNames]),
])
"""Спецификация настроек сервиса метрик

    Attributes
    ----------
    enable
        не писать в сервис метрик перехваченные от трассера данные
        и не инициализировать адаптер
    logging
        не писать в стандартный вывод диагностические сообщения от
        адаптера сервиса метрик
    url
        адрес сервиса метрик в формате "http://site.loc:1111"
    prefix
        добавлять ко всем ключам аннотации в начале данную строку
    hb_interval
        интервал проверки доступности сервиса (heartbeat)
    host
        часть строки url без номера порта
    port
        часть строки url, только номер порта
"""

StatsdOptions.__new__.__defaults__ = (  # type: ignore
    False, False, '', 'api', 2, None, None,
)
"""Настройки по умолчанию для сервиса метрик
"""

TracerOptions = NamedTuple('TracerOptions', [
    ('name', str),
    ('enable', bool),
    ('service_name', str),
    ('url', str),
    ('sample_rate', int),
    ('send_interval', int),
    ('skip_trace', Iterable[Any]),
    ('debug', bool),
    ('statsd', StatsdOptions),
    ('context_amqp_name', str),
])
"""Спецификация настроек сервиса метрик

    Attributes
    ----------
    name
        разновидность сервиса трассировки, пока всегда "zipkin"
    enable
        False - не писать события трассировки и не создавать адаптер,
        пропускать вызовы к обернутым функциям-точкам напрямую
    service_name
        название приложения в контексте трассера
    url
        адрес сервиса трассировки в формате "http://site.loc:1111/path/path/"
    sample_rate
        доля зарегистрированных событий, отправляемых трассеру
    send_interval
        как часто отправлять собранные данные трассеру
    skip_trace
        какие URL входящих точек HTTP не трассировать
    debug
        False - подавлять диагностические сообщения в стандартный вывод
    statsd
        настройки сервиса метрик хранятся внутри настроек трассера
"""

TracerOptions.__new__.__defaults__ = (  # type: ignore
    'zipkin', False, UNKNOWN_NAME, '', 1, 3, (), False, StatsdOptions(
        *StatsdOptions.__new__.__defaults__  # type: ignore
    ),
    None,
)
"""Настройки по умолчанию для трассера
"""


###############################################################################
# Варианты участков


# noinspection PyUnresolvedReferences
class SpanSide(EnumAuto):
    """Варианты направления точек

    Attributes
    ----------
    ALL
        любое направление, полезно для настройки правил извлечения содержимого
    IN
        входящая точка, запрос к нашему приложению со стороны
    OUT
        входящая точка, запрос от нашего приложения к стороннему
    """
    ALL = ()
    IN = ()
    OUT = ()
    MID = ()

# noinspection PyUnresolvedReferences
class APIKind(EnumAuto):
    """Варианты направления точек

    Attributes
    ----------
    ALL
        любое направление, полезно для настройки правил извлечения содержимого
    HTTP
        любые запросы по данному протоколу
    AMQP
        прием и отправка сообщений-задач через RabbitMQ очередь
    DB
        исходящие через адаптер базы данных запросы
    """
    ALL = ()
    HTTP = ()
    AMQP = ()
    RETASK = ()
    DB = ()
    INNER_RETRY = ()
    INNER_SHUTDOWN = ()
    LOG = ()


class Part(EnumAuto):
    OPEN = ()
    CLOSE = ()
    CLOSE_AFTER = ()


Variant = NamedTuple('Variant', [
    ('span_side', SpanSide),
    ('api_kind', APIKind),
])
"""Задаёт определённые разновидности точек по направлению и виду интерфейса

    Применяется для:

    * задания конкретного вида обернутой точки
    * задания вида или видов точек, к которым применяется правило извлечения
    содержимого

    Attributes
    ----------
    span_side
        направление
    api_kind
        вид интерфейса
"""

Variant.__new__.__defaults__ = (SpanSide.ALL, APIKind.ALL)  # type: ignore
"""Настройки по умолчанию для варианта
"""

###############################################################################
# Структура настройки источника и назначения извлекаемых данных


# noinspection PyUnresolvedReferences
class OriginSection(EnumAuto):
    """Разделы источников извлекаемых данных

    Состоят из данных, имеющихся в оборачиваемой точке и из данных,
    создаваемых самой библиотекой. В действительности указывают на
    конкретные атрибуты класса управления точкой

    Attributes
    ----------
    POINT_ARGS
        действительные аргументы обернутой точки
        доступны, начиная с фазы INIT
    POINT_RESULT
        действительный возвращаемый результат обернутой точки
        доступны, начиная с фазы POST
    POINT_REF
        ссылка на саму обернутую точку (метод или функцию)
        доступны, начиная с фазы INIT
    CLIENT
        клиентский объект для доступа к экземпляру запроса и пр.
        доступны, начиная с фазы INIT
    ADAPTER
        обертка трассера из данной библиотеки
        доступны, начиная с фазы INIT
    PROCESSOR
        объект управления извлечением
        доступны, начиная с фазы INIT
    CALL_STACK
        сокращённый стек вызовов перед входом в точку
        доступны, начиная с фазы INIT
    REUSE
        словарь переиспользуемых значений
        доступны, начиная с фазы PRE
    SPAN
        ссылка на объект участка
        доступны, начиная с фазы PRE
    """
    POINT_ARGS = ()
    POINT_RESULT = ()
    POINT_REF = ()
    CLIENT = ()
    ADAPTER = ()
    ENGINE = ()
    CALL_STACK = ()
    REUSE = ()
    SPAN = ()
    LOGS = ()


Origin = NamedTuple('Origin', [
    ('section', OriginSection),
    ('getter', Union[str, Callable]),
])
"""Настройка источника извлечения данных

    Attributes
    ----------
    section
        секция - указатель на атрибут менеджера точки, где содержатся данные
    getter
        функция, принимающая на вход ссылку на секцию и возвращающая
        извлеченное значение, либо строка - наименование атрибута секции,
        содержащего данные
"""


# noinspection PyUnresolvedReferences
class DestinationSection(EnumAuto):
    """Разделы мест назначения извлекаемых данных

    Задают в какие части участка или в какие внутренние атрибуты попадут
    извлеченные данные

    Attributes
    ----------
    SPAN_TAGS
        Помещённые сюда строки, появятся в заголовке участка
        Размещает SpanGeneral
    SPAN_LOGS
        Помещённые сюда строки, появятся в аннотации участка
        Размещает SpanGeneral
    SPAN_NAME
        Помещённые сюда строки, появятся в названии участка
        Размещает SpanGeneral
    POINT_ARGS
        Запись в аргументы, передаваемые обёрнутой точке. !Внимание! Это
        единственное назначение, которое может непосредственно повлиять на
        работу клиентской программы
        Размещает PointAccessor
    ADAPTER
        Запись в атрибуты собственного адаптера. Забыл зачем потребовалось.
        Размещает PointAccessor
    REUSE
        Запись промежуточного хранения и повторного использования в других
        обработчиках уже извлечённых данных
        Размещает PointAccessor
    ALL
        Используется в командах, для указания, что она относится ко всем
        назначениям, не используется в конкретной схеме
        Мета-назначение, данные не размещаются

    """
    SPAN_TAGS = ()
    SPAN_LOGS = ()
    SPAN_NAME = ()
    POINT_ARGS = ()
    ADAPTER = ()
    REUSE = ()
    DEBUG = ()
    ALL = ()


Destination = NamedTuple('Destination', [
    ('section', DestinationSection),
    ('name', Optional[str]),
])
"""Настройка назначения извлечения данных

    Для настройки извлечения данный тип является ключом, то есть для каждого
    назначения используется только одна настройка

    Attributes
    ----------
    section
        секция - раздел места назначения извлекаемых данных
    name
        наименование атрибута, не для всех секций имеет значение
"""

Destination.__new__.__defaults__ = (None,)  # type: ignore
"""Настройки по умолчанию для назначения извлекаемых данных
"""

###############################################################################
# Информация по обернутой точке

PointArguments = NamedTuple('PointArguments', [

])


PointContext = NamedTuple('PointContext', [
    ("point_ref", Callable),
    ("adapter", 'TracerWrapper'),
    ("engine", 'SchemaEngine'),
    ("span", Optional['SpanGeneral']),
    ("point_args", Optional[Dict[str, Any]]),
    ("point_result", Optional[Any]),
    ("client", Optional[Any]),
    ("call_stack", Optional[Sequence]),
    ("reuse", Optional[Dict[str, Any]]),
    ("debug", Optional[Dict[str, Any]]),
    ("headers", Optional[Dict[str, Any]]),
    ("span_tags", Optional[Dict[str, str]]),
    ("span_logs", Optional[Sequence[str]]),
    ("span_name", Optional[Dict[str, str]]),
])
"""Контекст оборачиваемой точки вызова

    Структурой этого типа обмениваются аксессор точки и механизм извлечения,
    аксессор заполняет её исходными данными, механизм пишет в неё
    извлечённые, а также изменения в исходные данные. Применением этих
    данных к состоянию приложения и к отправляемым на трассер участкам
    занимается аксессор точки, формированием - механизм извлечения.

    Attributes
    ----------
        Все секции источников и назначения, кроме обощающих
"""

PointContext.__new__.__defaults__ = (None,) * 11  # type: ignore
"""Настройки по умолчанию для контекста точки, стек вызовов необязателен
"""


###############################################################################
# Структура данных фаз извлечения наполнения


# noinspection PyUnresolvedReferences
class Stage(EnumAuto):
    """Фазы извлечения содержимого участка

    На какой стадии извлекается содержимое (пост- или пре-) зависит от
    автоматического отнесения секции конкретной настройки извлечения к той или
    иной фазе или от явного указания фазы этой настройки

    Attributes
    ----------
    INIT
        перед вызовом до создания участка трассировки
    PRE
        перед вызовом после создания участка трассировки
    POST
        после вызова обернутой точки, доступны результаты её работы
    """
    INIT = ()
    PRE = ()
    POST = ()


MethodNameToStage = Dict[str, Stage]
"""Отнесение методов класса управления участком к фазам обработки наполнения
"""


###############################################################################
# Настройка обработки наполнения участков


# noinspection PyUnresolvedReferences
class PipeCommand(EnumAuto):
    """Значения командного элемента

    Использование элемента схемы как директивы управления

    Attributes
    ----------
    SKIP_LEVELS_BELOW
        Не использовать схемы того же варианта с более низким приоритетом
    SKIP_SECRET_MASK
        Не применять маскирование определённых полей дялзаданных нзначений
    """
    SKIP_LEVELS_BELOW = ()
    SKIP_SECRET_MASK = ()
    TEE = ()
    STOP = ()


TeeDescriptor = Dict[Union[OriginSection, DestinationSection], Any]
"""Структура упаковки дополнительных данных

    Указатель на то, куда их записать отображается на сами данные
"""

PipelineTee = NamedTuple('PipelineTee', [
    ('main_story', Any),
    ('side_story', TeeDescriptor),
])
"""Настройка дополнительной записи извлеченных данных посреди процесса
обработки

    Если функция конвейера вернет данные, обернутые в этот объект, то часть
    данных будет перезаписана в источнике или назначении. Что и чем будет
    перезаписано управляется содержимым side_story

    Этот тип предназначен для:
    * Отправить собранные значимые данные в метки участка
    * Добавить в HTTP заголовки запроса элементы трассера
    * Сохранить извлеченные данные для переиспользования другим правилом
    извлечения

Attributes
----------
main_story
    данные, идущие дальше по конвейеру
side_story
    куда и какие промежуточные данные записывать
"""

Origins = Tuple[Origin, ...]
"""Список источников данных
"""
Pipeline = Tuple[Union[Callable, PipeCommand, Destination], ...]
"""Список методов обработки извлечённых данных
"""

Rule = NamedTuple('SchemaRule', [
    ('destination', Destination),
    ('origins', Origins),
    ('pipeline', Pipeline),
    ('stage', Stage),
    ('description', Optional[str]),
])
"""Настройка извлечения, базовый элемент схемы

Тип элемента описания:
* в какой элемент содержимого участка их писать (секция и необязательное
наименование)
* откуда получать данные для заполнения (секция: SourceSection и путь:
строка или функция)
* как их при этом обрабатывать
* описание для справки
* необязательное явное указание этапа применения

Attributes
----------
description
    необязательное описание для документирования и ориентирования
stage
    явное указание фазы, в которой будет работать данная
    настройка
destination
    указывает секцию и наименование места, куда будут помещены извлеченные
    данные
origins
    указывает секцию и функция получения исходных данных
pipeline
    список методов, через обработку которыми проходит по цепочке данные
skip_pipe
    методы обработки, которые адо пропустить
"""

Rule.__new__.__defaults__ = ('', )  # type: ignore
"""Настройки по умолчанию для назначения извлекаемых данных
"""

RuleSet = Tuple[Rule, ...]
Extractors = Dict[Stage, RuleSet]
Schema = Dict[Variant, RuleSet]
"""Схема извлечения данных

    Отображение вариантов на списки настроек
    извлекаемых значений
"""
