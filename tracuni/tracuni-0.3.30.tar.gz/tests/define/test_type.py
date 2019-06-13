#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Тесты модуля типов

"""

import sys
from enum import Enum

from typing import (
    Sequence,
    Optional,
    Union,
    Callable,
)

import pytest

from tracuni import trac_uni
from tracuni.trac_uni import TracerOptions, StatsdOptions

# pytest.skip('skipping {} tests'.format(__name__), allow_module_level=True)


###############################################################################
# Настройки трассера и сервиса сбора метрик


@pytest.fixture
def default_tracer_options(monkeypatch, unknown_name):
    """Настройки трассера со значениями по умолчанию
    """
    # if 'trac_uni.define.const' in sys.modules:
    #     del sys.modules['trac_uni.define.const']
    # mocker.patch('trac_uni.define.const.UNKNOWN_NAME', unknown_name)
    monkeypatch.setattr(
        trac_uni.define.type.TracerOptions.__new__,
        '__defaults__',
        (
            'zipkin', False, unknown_name, '', 1, 3, (), False,
            StatsdOptions(
                *StatsdOptions.__new__.__defaults__
            ),
        ),
    )
    return TracerOptions()


@pytest.fixture
def default_statsd_options():
    """Настройки сервиса метрик со значениями по умолчанию
    """
    from tracuni.trac_uni import StatsdOptions
    return StatsdOptions()


@pytest.fixture
def unknown_name():
    """Тестовое имя для импортируемого из модуля констант
    """
    return "some_ludicrous_service_name"


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test_tracer_default_options(
    monkeypatch,
    default_tracer_options,
    default_statsd_options,
    unknown_name,
    is_named_tuple_class,
):
    """Проверка настроек по умолчанию для трассера
    """
    # default_tracer_options = TracerOptions()
    assert is_named_tuple_class(type(default_tracer_options))
    assert default_tracer_options.name == 'zipkin'
    assert default_tracer_options.enable is False
    assert default_tracer_options.service_name == unknown_name
    assert default_tracer_options.url == ''
    assert default_tracer_options.sample_rate == 1
    assert default_tracer_options.send_interval == 3
    assert isinstance(default_tracer_options.skip_trace, Sequence)
    assert len(default_tracer_options.skip_trace) == 0
    assert default_tracer_options.debug is False
    assert hasattr(default_tracer_options, 'statsd')
    assert isinstance(
        default_tracer_options.statsd, type(default_statsd_options)
    )


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test_statsd_default_options(default_statsd_options, is_named_tuple_class):
    """Проверка настроек по умолчанию для сервиса метрик
    """
    assert is_named_tuple_class(type(default_statsd_options))
    assert default_statsd_options.enable is False
    assert default_statsd_options.logging is False
    assert default_statsd_options.url == ''
    assert default_statsd_options.prefix == 'api'
    assert default_statsd_options.hb_interval == 2
    assert default_statsd_options.host is None
    assert default_statsd_options.port is None


###############################################################################
# Варианты участков


@pytest.fixture
def default_variant():
    """Создание экземпляра варианта точки по умолчанию
    """
    from tracuni.trac_uni import (
        Variant,
    )
    return Variant()


@pytest.fixture
def variant_types():
    """Импорт типов варианта точки
    """
    # if 'trac_uni.define.type' in sys.modules:
    #     del sys.modules['trac_uni.define.type']
    from tracuni.trac_uni import (
        Variant,
        SpanSide,
        APIKind,
    )
    return [Variant, SpanSide, APIKind]


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test_auto_enum(variant_types):
    v_t, side_t, kind_t = variant_types
    assert side_t.IN < side_t.OUT
    with pytest.raises(TypeError) as exc_info:
        res = side_t.IN > 1
        del res
    assert exc_info


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test_variant_type(variant_types, is_named_tuple_class):
    """Тип варианта содержит данные о направлении и виде интерфейса точки
    """
    variant_type, _, _ = variant_types
    assert is_named_tuple_class(variant_type)
    assert hasattr(variant_type, 'span_side')
    assert hasattr(variant_type, 'api_kind')


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test_span_side_type(variant_types):
    """Существуют ожидаемые типы направления точки
    """
    _, span_side_type, _ = variant_types
    assert issubclass(span_side_type, Enum)
    assert hasattr(span_side_type, 'ALL')
    assert hasattr(span_side_type, 'SERVER')
    assert hasattr(span_side_type, 'CLIENT')
    assert hasattr(span_side_type, 'INCOMING')
    assert hasattr(span_side_type, 'OUTGOING')
    assert hasattr(span_side_type, 'IN')
    assert hasattr(span_side_type, 'OUT')


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test_api_kind_type(variant_types):
    """Существуют ожидаемые типы интерфейса точки
    """
    _, _, api_kind_type = variant_types
    assert issubclass(api_kind_type, Enum)
    assert hasattr(api_kind_type, 'ALL')
    assert hasattr(api_kind_type, 'HTTP')
    assert hasattr(api_kind_type, 'AMQP')
    assert hasattr(api_kind_type, 'DB')


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test_default_variant(default_variant):
    """По умолчанию создаётся вариант, относящийся ко всем разновидностям точек
    """
    assert str(default_variant.span_side) == 'SpanSide.ALL'
    assert str(default_variant.api_kind) == 'APIKind.ALL'


###############################################################################
# Информация по обернутой точке


@pytest.fixture
def point_context_type(mocker):
    """Импорт типа контекста точки
    """
    if 'trac_uni.type' in sys.modules:
        del sys.modules['trac_uni.type']
    mocker.patch('typing.TYPE_CHECKING', True)
    from tracuni.trac_uni import (
        PointContext,
    )
    return PointContext


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test_point_context_type(point_context_type, is_named_tuple_class):
    """"Существует ожидаемый тип контекста точки
    """
    assert is_named_tuple_class(point_context_type)


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test_point_context_instance_miss_required(point_context_type):
    """Должен валиться если не заданы все обязательные параметры
    """
    with pytest.raises(TypeError):
        point = point_context_type(
        )
        del point
    with pytest.raises(TypeError):
        point = point_context_type(
            POINT_ARGS={'a': 'a'}
        )
        del point


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test_point_context_instance(point_context_type):
    """Можно создать экземпляр контекста точки
    """

    def test_func(*args, **kwargs):
        return kwargs['x'] + sum(args)

    point = point_context_type(
        point_args={'x': 10},
        point_ref=test_func,
        adapter=object(),
        engine=object(),
        span=object(),
    )
    assert point.point_ref(*[10, 22], **point.point_args) == 42


###############################################################################
# Структура конфигурации обработки наполнения участков


@pytest.fixture
def stage_type():
    """Импорт типа фаз извлечения содержимого
    """
    from tracuni.trac_uni import (
        Stage
    )
    return Stage


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test_stage_type(stage_type):
    """Существуют ожидаемые виды фаз извлечения
    """
    assert issubclass(stage_type, Enum)
    assert hasattr(stage_type, 'INIT')
    assert hasattr(stage_type, 'PRE')
    assert hasattr(stage_type, 'POST')


@pytest.fixture
def origin_section_type():
    """Импорт типа секций источников извлекаемых данных
    """
    from tracuni.trac_uni import (
        OriginSection
    )
    return OriginSection


@pytest.fixture
def origin_type():
    """Импорт типа описания извлекаемых данных
    """
    from tracuni.trac_uni import (
        Origin
    )
    return Origin


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test_origin_section_type(origin_section_type):
    """Существуют ожидаемые секции источников
    """
    assert issubclass(origin_section_type, Enum)
    assert hasattr(origin_section_type, 'POINT_ARGS')
    assert hasattr(origin_section_type, 'POINT_RESULT')
    assert hasattr(origin_section_type, 'POINT_REF')
    assert hasattr(origin_section_type, 'CLIENT')
    assert hasattr(origin_section_type, 'ADAPTER')
    assert hasattr(origin_section_type, 'ENGINE')
    assert hasattr(origin_section_type, 'CALL_STACK')
    assert hasattr(origin_section_type, 'REUSE')
    assert hasattr(origin_section_type, 'SPAN')


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test_origin_type(origin_type, origin_section_type, is_named_tuple_class):
    """"Существует ожидаемый тип настройки источника извлекаемых данных
    """
    assert is_named_tuple_class(origin_type)
    assert hasattr(origin_type, 'section')
    assert origin_type.__annotations__['section'] == origin_section_type
    assert hasattr(origin_type, 'getter')
    assert origin_type.__annotations__['getter'] == Union[str, Callable]


@pytest.fixture
def destination_section_type():
    """Импорт типа секций назначения извлекаемых данных
    """
    from tracuni.trac_uni import (
        DestinationSection
    )
    return DestinationSection


@pytest.fixture
def destination_type():
    """Импорт типа наименования атрибута назначения
    """
    from tracuni.trac_uni import (
        Destination
    )
    return Destination


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test_destination_section_type(destination_section_type):
    """Существуют ожидаемые секции назначения
    """
    assert issubclass(destination_section_type, Enum)
    assert hasattr(destination_section_type, 'TAGS')
    assert hasattr(destination_section_type, 'LOGS')
    assert hasattr(destination_section_type, 'SPAN_ID')
    assert hasattr(destination_section_type, 'ALL')


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test_destination_type(destination_type,
                          destination_section_type,
                          is_named_tuple_class):
    """"Существует ожидаемый тип настройки назначения извлекаемых данных
    """
    assert is_named_tuple_class(destination_type)
    assert hasattr(destination_type, 'section')
    assert (
        destination_type.__annotations__['section'] == destination_section_type
    )
    assert hasattr(destination_type, 'name')
    assert destination_type.__annotations__['name'] == Optional[str]


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test_destination_instance_miss_required(destination_type):
    """Должен валиться если не заданы все обязательные параметры
    """
    with pytest.raises(TypeError):
        destination = destination_type()
        del destination


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test_destination_instance(destination_type, destination_section_type):
    """Можно создать экземпляр собранного содержимого
    """
    destination = destination_type(
        section=destination_section_type.TAGS,
    )
    assert (
        str(destination) == 'Destination(section=<DestinationSection.TAGS: '
                            '1>, name=None)'
    )


@pytest.fixture
def tee_types():
    """Импорт типа наименования атрибута назначения
    """
    from tracuni.trac_uni import (
        PipelineTee,
        TeeDescriptor,
    )
    return PipelineTee, TeeDescriptor


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test_tee_type(tee_types, is_named_tuple_class):
    """Существует ожидаемый тип настройки ответвлённой записи
    """
    tee_type, tee_descriptor_type = tee_types
    assert is_named_tuple_class(tee_type)
    assert hasattr(tee_type, 'main_story')
    assert hasattr(tee_type, 'side_story')
    assert tee_type.__annotations__['side_story'] == tee_descriptor_type


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test_tee_instance_miss_required(tee_types):
    """Должен валиться если не заданы все обязательные параметры
    """
    tee_type, _ = tee_types
    with pytest.raises(TypeError):
        tee = tee_type()
        del tee


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test_tee_instance(
    tee_types,
    origin_type,
    origin_section_type,
    destination_type,
    destination_section_type,
):
    """Можно создать экземпляр настройки ответвлённой записи
    """
    tee_type, _ = tee_types
    tee = tee_type(
        main_story='11',
        side_story={
            origin_type(origin_section_type.CLIENT, 'headers'): {
                'header': 'content'
            }
        }
    )
    del tee


@pytest.fixture
def stage_maps():
    """Импорт типа секций назначения извлекаемых данных
    """
    from tracuni.trac_uni import (
        stage_to_sections,
        method_to_stage,
        Stage,
    )
    expected_keys = (Stage.INIT, Stage.POST)
    return method_to_stage, stage_to_sections, expected_keys


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test_method_stage_map(stage_maps):
    method_stage_map, stage_sections_map, expected_keys = stage_maps
    assert type(method_stage_map) == dict
    assert type(stage_sections_map) == dict
    assert not set(stage_sections_map.keys()) ^ set(expected_keys)


###############################################################################
# Настройка обработки наполнения участков


@pytest.fixture
def extractables_types():
    """Импорт типа обработки
    """
    from tracuni.trac_uni import (
        Rule,
        Origins,
        Pipeline,
        Schema,
    )
    return Rule, Origins, Pipeline, Schema


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test_extractables_type(extractables_types,
                           stage_type,
                           destination_type,
                           is_named_tuple_class):
    """Существует ожидаемый тип настройки настройки извлечения данных участка
    """
    extract_type, origins_type, extract_proc, _ = extractables_types
    assert is_named_tuple_class(extract_type)
    assert hasattr(extract_type, 'destination')
    assert extract_type.__annotations__['destination'] == destination_type
    assert hasattr(extract_type, 'origins')
    assert extract_type.__annotations__['origins'] == origins_type
    assert hasattr(extract_type, 'pipeline')
    assert extract_type.__annotations__['pipeline'] == extract_proc
    assert hasattr(extract_type, 'description')
    assert extract_type.__annotations__['description'] == Optional[str]
    assert hasattr(extract_type, 'stage')
    assert extract_type.__annotations__['stage'] == Optional[stage_type]


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test_extractables(extractables_types,
                      variant_types,
                      stage_type,
                      destination_type,
                      destination_section_type,
                      origin_type,
                      origin_section_type,
                      ):
    """Создаются разные варианты настройки извлечения данных участка
    """
    extract_type, _, _, setup_type = extractables_types
    variant_type, span_side_type, api_kind_type = variant_types

    setup_empty = {

    }  # type: setup_type
    assert str(setup_empty) == '{}'
    del setup_empty

    setup_some = {  # type: setup_type
        variant_type(): (
            extract_type(
                description='test',
                destination=destination_type(
                    section=destination_section_type.LOGS,
                    name='some'
                ),
                origins=(
                    origin_type(
                        section=origin_section_type.SPAN,
                        getter='id'
                    )
                ),
                pipeline=(),
            ),
        )
    }
    assert isinstance(setup_some, dict)
    del setup_some

    setup_all = {  # type: setup_type
        variant_type(): (
            extract_type(
                destination=destination_type(
                    section=destination_section_type.LOGS,
                    name='some'
                ),
                origins=(
                    origin_type(
                        section=origin_section_type.POINT_ARGS,
                        getter=lambda v: str(v)
                    )
                ),
                pipeline=(),
            ),
            extract_type(
                description="some",
                destination=destination_type(
                    section=destination_section_type.TAGS,
                    name='some'
                ),
                origins=(
                    origin_type(
                        section=origin_section_type.SPAN,
                        getter='id'
                    )
                ),
                pipeline=(),
            ),
            extract_type(
                destination=destination_type(
                    section=destination_section_type.SPAN_ID,
                    name='some'
                ),
                origins=(
                    origin_type(
                        section=origin_section_type.POINT_RESULT,
                        getter='id'
                    ),
                    origin_type(
                        section=origin_section_type.POINT_REF,
                        getter='id'
                    ),
                    origin_type(
                        section=origin_section_type.CLIENT,
                        getter='id'
                    ),
                ),
                pipeline=(),
                stage=stage_type.POST,
            ),
            extract_type(
                destination=destination_type(
                    section=destination_section_type.TAGS,
                    name='some'
                ),
                origins=(
                    origin_type(
                        section=origin_section_type.REUSE,
                        getter='id'
                    ),
                    origin_type(
                        section=origin_section_type.ADAPTER,
                        getter='id'
                    ),
                    origin_type(
                        section=origin_section_type.ENGINE,
                        getter='id'
                    ),
                ),
                pipeline=(
                    lambda *args: ','.join(str(el) for el in args)
                ),
            ),
            extract_type(
                destination=destination_type(
                    section=destination_section_type.LOGS,
                    name='some'
                ),
                origins=(
                    origin_type(
                        section=origin_section_type.CALL_STACK,
                        getter='id'
                    )
                ),
                pipeline=(),
            ),
            extract_type(
                destination=destination_type(
                    section=destination_section_type.TAGS,
                    name='some'
                ),
                origins=(
                    origin_type(
                        section=origin_section_type.SPAN,
                        getter='id'
                    )
                ),
                pipeline=(),
            ),
        )
    }
    assert isinstance(setup_all, dict)
    del setup_all
