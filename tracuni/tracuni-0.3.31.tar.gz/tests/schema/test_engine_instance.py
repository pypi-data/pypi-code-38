#!/usr/bin/env python
# -*- coding: utf-8 -*-
# noinspection PyProtectedMember

"""Проверка создания экземпляров обработчиков схем
"""

from tracuni.trac_uni import (
    SpanSide,
    APIKind,
    Stage,
)

import pytest


# pytest.skip('skipping {} tests'.format(__name__), allow_module_level=True)


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test_engine_instance(
    engine_types,
    simple_engine,
):
    """Создание процессора схемы

        * Создаётся экземпляр процессора
        * Инициализируется выбранным вариантом
        * Получает стандартную схему
        * Раскладывает схему для данного варианта
    """
    concrete_type = engine_types[0]
    p = simple_engine
    assert (
        isinstance(p, concrete_type)
    ), "Создаётся экземпляр процессора"
    assert (
        p.secret_mask_method_name == 'test_pipe_secret'
    ), "Есть корректный атрибут наименования модификатора маскирования"
    assert (
        p.skip_secret_destinations == []
    ), "Есть корректный атрибут списка отмены маскирования"
    assert (
        {p.method_to_stage.values()}
        ^
        {Stage.INIT, Stage.PRE, Stage.POST}
    ), "Есть корректный атрибут отображения наименований методов точки на фазы"
    assert (
        p.extractors
    ), "Есть непустой атрибут списков правил по фазам"


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test_feed_instance_no_custom_rules(
    engine_types,
    variants,
    mock_standard_schema,
):
    """Создание процессора схемы

        * Создаётся экземпляр процессора
        * Инициализируется выбранным вариантом
        * Получает стандартную схему
        * Раскладывает схему для данного варианта
    """
    feed_t = engine_types[2]
    c = feed_t(
        variants[0],
    )
    assert (
        isinstance(c, feed_t)
    ), "Создаётся экземпляр поставщика схем"
    assert (
        hasattr(c, 'variant')
    ), "В созданном экземпляре процессоре есть вариант"
    assert (
        c.variant.api_kind == APIKind.HTTP
    ), "В созданном экземпляре процессоре есть вариант переданного " \
       "вида интерфейса"
    assert (
        c.variant.span_side == SpanSide.IN
    ), "В созданном экземпляре процессоре есть вариант переданного " \
       "направления"
    assert (
        [
            (
                rule.destination,
                rule.stage,
                [o.section for o in rule.origins],
                len(rule.pipeline),
            )
            for ruleset in mock_standard_schema.values()
            for rule in ruleset
        ]
        ==
        [
            (
                rule.destination,
                rule.stage,
                [o.section for o in rule.origins],
                len(rule.pipeline),
            )
            for ruleset in c.standard_schema.values()
            for rule in ruleset
        ]
    ), "Импортируется нужная стандартная схема"


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test_feed_instance_custom_rules(
    engine_types,
    mock_standard_schema,
    both_custom_rules_engine,
):
    feed_t = engine_types[2]
    c = feed_t(
        both_custom_rules_engine.schema_feed.variant,
        both_custom_rules_engine.schema_feed.point_ruleset,
        both_custom_rules_engine.schema_feed.custom_schema,
    )
    assert (
        c.point_ruleset
        ==
        mock_standard_schema[tuple(mock_standard_schema.keys())[0]]
    ), "В объекте сохраняется пользовательская схема точки"
    assert (
        c.custom_schema
        ==
        mock_standard_schema
    ), "В объекте сохраняется пользовательская карта схем"


# @pytest.mark.skip(reason="get out of the other tests' way to debug them")
def test_engine_feed_no_variant(engine_types):
    e_t, _, _, err = engine_types
    expected_err = err.ProcessorInitNoneOrWrongTypeVariant
    with pytest.raises(expected_err):
        v = e_t(1)
        del v
    with pytest.raises(expected_err):
        # noinspection PyArgumentList
        v = e_t()  # noqa
        del v
    with pytest.raises(expected_err):
        v = e_t(variant=1)
        del v


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test_processor_wrong_schema(engine_types, variants):
    e_t, _, _, err = engine_types
    with pytest.raises(err.ProcessorInitWrongTypeCustomSchema):
        v = e_t(variant=variants[0], point_ruleset=1)
        del v
    with pytest.raises(err.ProcessorInitWrongTypeCustomSchema):
        v = e_t(variant=variants[0], custom_schema=1)
        del v
