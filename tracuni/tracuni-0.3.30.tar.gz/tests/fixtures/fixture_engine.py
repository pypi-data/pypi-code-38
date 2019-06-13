#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Тестовые типы и экземпляры обрабтчика схем
"""

import sys
import pytest


@pytest.fixture
def engine_types(mocker, mock_standard_schema, stage_to_sections):
    """Импорт мета-класса, осуществляющего кеширование экземпляров процессоров
    схем
    """
    if 'trac_uni.schema.standard' in sys.modules:
        del sys.modules['trac_uni.schema.standard']
    if 'trac_uni.schema.engine.engine' in sys.modules:
        del sys.modules['trac_uni.schema.engine.engine']
    mocker.patch(
        'typing.TYPE_CHECKING',
        True
    )

    # noinspection PyUnresolvedReferences
    from tracuni import trac_uni

    mocker.patch(
        'trac_uni.schema.standard.standard_schema',
        mock_standard_schema
    )
    mocker.patch(
        'trac_uni.schema.standard.stage_to_sections',
        stage_to_sections
    )
    mocker.patch(
        'trac_uni.schema.standard.secret_mask_method_name',
        'test_pipe_secret'
    )
    mocker.patch(
        'trac_uni.schema.standard.secret_mask_method_name',
        'test_pipe_secret'
    )

    from tracuni.trac_uni import SchemaEngineCache  # noqa
    from tracuni.trac_uni import SchemaEngine
    from tracuni.trac_uni import SchemaEngineFeed
    from tracuni import trac_uni as err

    return SchemaEngine, SchemaEngineCache, SchemaEngineFeed, err


@pytest.fixture
def simple_engine(engine_types, variants):
    return engine_types[0](variants[0])


@pytest.fixture
def both_custom_rules_engine(engine_types, variants, mock_standard_schema):
    return engine_types[0](
        variants[0],
        point_ruleset=mock_standard_schema[variants[0]],
        custom_schema=mock_standard_schema,
    )
