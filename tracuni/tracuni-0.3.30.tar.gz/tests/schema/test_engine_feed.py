#!/usr/bin/env python
# -*- coding: utf-8 -*-
# noinspection PyProtectedMember

"""Проверка поставщика схем
"""

from collections import OrderedDict

from tracuni.trac_uni import (
    Destination,
    DestinationSection,
    PipeCommand,
    Stage,
)

# import pytest

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from tracuni.trac_uni import Extractors  # noqa


# pytest.skip('skipping {} tests'.format(__name__), allow_module_level=True)


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test__compose_variants(
    simple_engine,
    custom_plus_standard_schema_map,
):
    p = simple_engine

    custom_plus_standard_composed = tuple(
        p.schema_feed._compose_variants(el, tuple()) for el in
        custom_plus_standard_schema_map
    )

    schema_names = ''.join(el.description for el in (
        *custom_plus_standard_composed[0],
        *custom_plus_standard_composed[1],
    ))

    assert (
        schema_names == 'c1ac1bc2c3ac3bc4s1as1bs2s3as3bs4'
    ), "Работает отбор правил схем по варианту"


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test__group_by_stage(
    simple_engine,
    auto_stage_rules,
    stage_to_sections
):
    p = simple_engine

    assert (
        p.schema_feed.stage_to_sections == stage_to_sections
    ), "Используются нужные подставные данные по отношению секций к фазам"
    schema = tuple(
        el
        for tuple_el
        in tuple(OrderedDict(sorted(
            auto_stage_rules.items(), key=lambda x: x[0]
        )).values())
        for el in tuple_el
    )
    stage_to_schema = p.schema_feed._distribute_by_stages(schema)
    assert (
        len(stage_to_schema) == 3
    ), "Все фазы в отношении на месте"
    assert (
        not set(''.join(
            el.destination.name
            for el in stage_to_schema.get(Stage.INIT)
        )) ^ set('ab')
    ), "Правила фазы старта попали на своё место без лишних"
    assert (
        not set(''.join(
            el.destination.name
            for el in stage_to_schema.get(Stage.PRE)
        )) ^ set('cd')
    ), "Правила фазы вызова попали на своё место без лишних"
    assert (
        not set(''.join(
            el.destination.name
            for el in stage_to_schema.get(Stage.POST)
        )) ^ set('efg')
    ), "Правила фазы завершения попали на своё место без лишних"


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test__should_skip_level_below(
    simple_engine,
    gen_schema_rule,
):
    flag = simple_engine.schema_feed._should_skip_level_below()[1]
    assert bool(flag) is False,\
        "Пустая схема не содержит флага"
    flag = simple_engine.schema_feed._should_skip_level_below((
        gen_schema_rule('should_skip', Destination(
                section=DestinationSection.ALL
            ),
            pipeline=(PipeCommand.SKIP_LEVELS_BELOW,)
        ),
    ))[1]
    assert bool(flag) is True,\
        "Схема содержит флаг"
    flag = simple_engine.schema_feed._should_skip_level_below((
        gen_schema_rule('no_skip', Destination(
            section=DestinationSection.LOGS,
            name='no_skip'
        )),
    ))[1]
    assert bool(flag) is False,\
        "Схема не содержит флага"


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test_skip_all_levels_below(
    engine_types,
    gen_schema_rule,
    custom_plus_standard_schema_map,
    variants,
):
    p_t, *_ = engine_types
    p = p_t(
        variants[0],
        (
            gen_schema_rule('pc1'),
            gen_schema_rule('pc2', Destination(
                section=DestinationSection.POINT_ARGS,
                name='ARGS'
            )),
            gen_schema_rule('pc3'),
            gen_schema_rule('pc4skip', Destination(
                    section=DestinationSection.ALL
                ),
                pipeline=(PipeCommand.SKIP_LEVELS_BELOW,)
            ),
        ),
        custom_plus_standard_schema_map[0],
    )
    assert (
        not
        {
            el.description
            for tuple_el in p.extractors.values()
            for el in tuple_el
        }
        ^
        {'pc1', 'pc2'}
    ), "Если указана команда пропуска нижестоящих уровней в пользовательской" \
       "схеме точки, остаются только правила из пользовательской схемы"
    assert (not len(tuple(
        pipe
        for _, schema in p.extractors.items()
        for extractor in schema
        for pipe in extractor.pipeline
        if pipe == PipeCommand.SKIP_LEVELS_BELOW
    ))), "Правило-команда по игнорированию менее приоритетных должно быть " \
         "убрано из схемы после его применения"
    parsed_twice = p.schema_feed.parse()  # type: Extractors
    assert (
        not
        {
            el.description
            for tuple_el in parsed_twice.values()
            for el in tuple_el
        }
        ^
        {'pc1', 'pc2'}
    ), "И это, минутку внимания, должно быть идемпотентно"
