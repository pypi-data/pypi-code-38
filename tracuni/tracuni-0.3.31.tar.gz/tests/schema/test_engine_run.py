#!/usr/bin/env python
# -*- coding: utf-8 -*-
# noinspection PyProtectedMember

"""Проверка поставщика схем
"""

import types
from typing import Tuple

from tracuni.trac_uni import (
    Destination,
    DestinationSection,
    Origin,
    OriginSection,
    PipeCommand,
    Stage,
    PipelineTee,
    PointContext,
)
from tracuni.trac_uni import method_to_stage

import pytest


# pytest.skip('skipping {} tests'.format(__name__), allow_module_level=True)


@pytest.mark.asyncio
def test__skip_secret_use(
    engine_types,
    gen_schema_rule,
    variants,
    point_context,
):
    e_t, *_ = engine_types

    def test_pipe_secret(_):
        return "test"

    setup = (
        gen_schema_rule(
            destination=Destination(
                DestinationSection.ALL,
            ),
            pipeline=(PipeCommand.SKIP_LEVELS_BELOW,),
            stage=Stage.INIT,
        ),
        gen_schema_rule(
            origins=(Origin(OriginSection.POINT_ARGS, 'some'),),
            destination=Destination(
                DestinationSection.REUSE,
                "some",
            ),
            pipeline=(test_pipe_secret,),
            stage=Stage.INIT,
        ),
    )

    e = e_t(variants[0], point_ruleset=setup)
    init_stage_method_name = [
        k for k, v in method_to_stage.items()
        if v == Stage.INIT
    ][0]
    result = yield from e.extract(point_context, init_stage_method_name)
    assert result.reuse['some'] == 'test'


@pytest.mark.asyncio
def test__skip_secret_skip(
    engine_types,
    gen_schema_rule,
    variants,
    point_context,
):
    e_t, *_ = engine_types

    def test_pipe_secret(_):
        return "11"

    setup = (
        gen_schema_rule(
            destination=Destination(
                DestinationSection.ALL,
            ),
            pipeline=(PipeCommand.SKIP_LEVELS_BELOW,),
            stage=Stage.INIT,
        ),
        gen_schema_rule(
            origins=(Origin(OriginSection.POINT_ARGS, 'some'),),
            destination=Destination(
                DestinationSection.REUSE,
                "some",
            ),
            pipeline=(test_pipe_secret,),
            stage=Stage.INIT,
        ),
        gen_schema_rule(
            destination=Destination(
                DestinationSection.ALL,
            ),
            pipeline=(PipeCommand.SKIP_SECRET_MASK,)
        ),
    )

    e = e_t(variants[0], point_ruleset=setup)
    init_stage_method_name = [
        k for k, v in method_to_stage.items()
        if v == Stage.INIT
    ][0]
    result = yield from e.extract(point_context, init_stage_method_name)
    assert result.reuse['some'] != 'test'


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
@pytest.mark.asyncio
def test__should_skip_level_parse(
    engine_types,
    gen_schema_rule,
    custom_plus_standard_schema_map,
    variants,
    point_context,
):
    p_t, *_ = engine_types
    custom_schema = {
        variants[1]: (
            gen_schema_rule(
                destination=Destination(
                    DestinationSection.REUSE,
                    'test_override',
                ),
                origins=(Origin(
                    OriginSection.POINT_ARGS,
                    lambda _: "custom",
                ),),
                pipeline=(lambda x: x[0],),
            ),
            gen_schema_rule(
                destination=Destination(
                    DestinationSection.ALL,
                ),
                pipeline=(PipeCommand.SKIP_LEVELS_BELOW, lambda x: x,)
            ),
        ),
    }
    p = p_t(
        variants[1],
        custom_schema=custom_schema,
    )
    init_stage_method_name = [
        k for k, v in method_to_stage.items()
        if v == Stage.INIT
    ][0]
    point_context = yield from p.extract(point_context, init_stage_method_name)
    assert point_context.reuse['some'] == "value"
    assert point_context.reuse['test_override'] == "custom"


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
@pytest.mark.asyncio
def test__skip_from_custom_map_all(
    engine_types,
    gen_schema_rule,
    custom_plus_standard_schema_map,
    variants,
    point_context,
):
    p_t, *_ = engine_types
    custom_schema_map = {
        variants[1]: (
            gen_schema_rule(
                destination=Destination(
                    DestinationSection.REUSE,
                    'test_override',
                ),
                origins=(Origin(
                    OriginSection.POINT_ARGS,
                    lambda _: "custom",
                ),),
                pipeline=(lambda x: x[0],),
            ),
            gen_schema_rule(
                destination=Destination(
                    DestinationSection.ALL,
                ),
                pipeline=(PipeCommand.SKIP_LEVELS_BELOW, lambda x: x,)
            ),
        ),
    }
    p = p_t(
        variants[1],
        custom_schema=custom_schema_map,
    )
    init_stage_method_name = [
        k for k, v in method_to_stage.items()
        if v == Stage.INIT
    ][0]
    point_context = yield from p.extract(point_context, init_stage_method_name)
    assert point_context.reuse['some'] == "value"
    assert point_context.reuse['test_override'] == "custom"


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
@pytest.mark.asyncio
def test__skip_from_custom_map_specific(
    engine_types,
    gen_schema_rule,
    custom_plus_standard_schema_map,
    variants,
    point_context,
):
    p_t, *_ = engine_types
    custom_schema_map = {
        variants[1]: (
            gen_schema_rule(
                destination=Destination(
                    DestinationSection.TAGS,
                    'test_override',
                ),
                origins=(Origin(
                    OriginSection.POINT_ARGS,
                    lambda _: "custom",
                ),),
                pipeline=(lambda x: x[0],),
            ),
            gen_schema_rule(
                destination=Destination(
                    DestinationSection.REUSE,
                    name="test_override",
                ),
                pipeline=(PipeCommand.SKIP_LEVELS_BELOW, lambda x: x,)
            ),
        ),
    }
    p = p_t(
        variants[1],
        custom_schema=custom_schema_map,
    )
    init_stage_method_name = [
        k for k, v in method_to_stage.items()
        if v == Stage.INIT
    ][0]
    point_context = yield from p.extract(point_context, init_stage_method_name)
    assert 'test_override' not in point_context.reuse
    assert point_context.tags['test_override'] == "custom"
    assert point_context.logs == ["standard"]


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
@pytest.mark.asyncio
def test__extract_values_miss(
    simple_engine,
    gen_schema_rule,
    point_context,
):
    rule = gen_schema_rule(
        origins=(
            Origin(section=OriginSection.CLIENT, getter="some"),
            Origin(section=OriginSection.REUSE, getter="none"),
            Origin(section=OriginSection.CLIENT, getter="none"),
        ),
    )
    extracted = yield from simple_engine._extract_values(
        rule,
        point_context,
    )
    assert isinstance(extracted, tuple)
    assert len(extracted) == 0


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
@pytest.mark.asyncio
def test__extract_values_dict(
    simple_engine,
    gen_schema_rule,
    point_context,
):
    rule = gen_schema_rule(
        origins=(Origin(section=OriginSection.REUSE, getter="some"),),
    )
    extracted = yield from simple_engine._extract_values(
        rule,
        point_context,
    )
    assert isinstance(extracted, tuple)
    assert len(extracted) > 0
    assert extracted[0] == "value"


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
@pytest.mark.asyncio
def test__extract_values_obj(
    simple_engine,
    gen_schema_rule,
    point_context,
):
    rule = gen_schema_rule(
        origins=(Origin(section=OriginSection.SPAN, getter="some"),),
    )
    extracted = yield from simple_engine._extract_values(
        rule,
        point_context
    )
    assert isinstance(extracted, tuple)
    assert len(extracted) > 0
    assert extracted[0] == "value"


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
@pytest.mark.asyncio
def test__extract_values_coroutine(
    simple_engine,
    gen_schema_rule,
    point_context,
):
    @types.coroutine
    def g(come):
        yield
        return come.get('some')

    rule = gen_schema_rule(
        origins=(Origin(section=OriginSection.REUSE, getter=g),),
    )
    extracted = yield from simple_engine._extract_values(
        rule,
        point_context,
    )
    assert isinstance(extracted, tuple)
    assert len(extracted) > 0
    assert extracted[0] == "value"


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
@pytest.mark.asyncio
def test__extract_values_function(
    simple_engine,
    gen_schema_rule,
    point_context,
):
    def g(come):
        return come.get('some')

    rule = gen_schema_rule(
        origins=(Origin(section=OriginSection.REUSE, getter=g),),
    )
    extracted = yield from simple_engine._extract_values(
        rule,
        point_context,
    )
    assert isinstance(extracted, tuple)
    assert len(extracted) > 0
    assert extracted[0] == "value"


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
@pytest.mark.asyncio
def test__extract_values_root(
    simple_engine,
    gen_schema_rule,
    point_context,
):
    rule = gen_schema_rule(
        origins=(Origin(section=OriginSection.REUSE, getter="/"),),
    )
    extracted = yield from simple_engine._extract_values(
        rule,
        point_context,
    )
    assert isinstance(extracted, tuple)
    assert len(extracted) > 0
    assert isinstance(extracted[0], dict)
    assert extracted[0].get("some") == "value"


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test__pipe_values_instance(
    simple_engine,
    gen_schema_rule,
    point_context,
):
    v = simple_engine._pipe_values(gen_schema_rule(), 1, point_context)
    assert v.logs == [1]


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test__pipe_values_tee(
    simple_engine,
    gen_schema_rule,
    point_context,
):
    upd_point_context = {
        OriginSection.POINT_ARGS.name.lower(): "old_value",
        DestinationSection.LOGS.name.lower(): ["old_value"],
        DestinationSection.TAGS.name.lower(): {"a": "old_value"},
    }
    test_point_context = PointContext(**{
        **point_context._asdict(),
        **upd_point_context,
    })

    def pipe_tee(v):
        return PipelineTee(
            main_story=v,
            side_story={
                OriginSection.POINT_ARGS: v,
                DestinationSection.LOGS: [v],
            }
        )
    test_point_context = simple_engine._pipe_values(gen_schema_rule(
        destination=Destination(
            DestinationSection.TAGS,
            'b',
        ),
        pipeline=(pipe_tee,),
    ), "new_value", test_point_context)
    assert test_point_context.point_args == "new_value"
    assert test_point_context.logs == ["new_value"]
    assert test_point_context.tags == {"a": "old_value", "b": "new_value"}


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test__update_point_context_empty(
    simple_engine,
    gen_schema_rule,
    point_context,
    engine_types,
):
    err = engine_types[-1]
    test_point_context = PointContext(**point_context._asdict())
    simple_engine._update_point_context(
        gen_schema_rule(destination=Destination(DestinationSection.ALL)),
        test_point_context,
        "nothing",
    )
    assert point_context == test_point_context

    test_point_context = PointContext(**{
        **point_context._asdict(),
        **{
            'logs': 1
        },
    })
    with pytest.raises(
        err.ProcessorExtractCantSetDestinationAttr,
    ):
        simple_engine._update_point_context(
            gen_schema_rule(
                destination=Destination(
                    section=DestinationSection.LOGS,
                    name='test'
                ),
            ),
            test_point_context,
            "nothing",
        )

    class Test:
        pass
    test_point_context = PointContext(**{
        **point_context._asdict(),
        **{
            'logs': Test()
        },
    })
    res = simple_engine._update_point_context(
        gen_schema_rule(
            destination=Destination(
                section=DestinationSection.LOGS,
                name="test"
            ),
        ),
        test_point_context,
        "some",
    )
    assert res.logs.test == "some"


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
@pytest.mark.asyncio
def test_extract(
    engine_types,
    variants,
    gen_schema_rule,
    point_context,
):

    def pipe_rev(x: Tuple[str]):
        return ''.join(reversed(x[0]))

    p_t = engine_types[0]
    p = p_t(
        variants[0],
        (
            gen_schema_rule(
                'ignore other rules',
                destination=Destination(
                    section=DestinationSection.ALL
                ),
                pipeline=(PipeCommand.SKIP_LEVELS_BELOW,)
            ),
            gen_schema_rule(
                'collect logs',
                destination=Destination(
                    section=DestinationSection.LOGS,
                    name="first",
                ),
                origins=(
                    Origin(
                        section=OriginSection.POINT_ARGS,
                        getter='some',
                    ),
                ),
                pipeline=(pipe_rev,),
                stage=Stage.INIT,
            ),
            gen_schema_rule(
                'collect logs',
                destination=Destination(
                    section=DestinationSection.LOGS,
                    name="second",
                ),
                origins=(
                    Origin(
                        section=OriginSection.LOGS,
                        getter=lambda x: x[0],
                    ),
                ),
                pipeline=(pipe_rev,),
                stage=Stage.PRE,
            ),
            gen_schema_rule(
                'collect logs',
                destination=Destination(
                    section=DestinationSection.LOGS,
                    name="third",
                ),
                origins=(
                    Origin(
                        section=OriginSection.LOGS,
                        getter=lambda x: None,
                    ),
                ),
                pipeline=(lambda x: x,),
                stage=Stage.POST,
            ),
        ),

    )
    init_stage_method_name = [
        k for k, v in method_to_stage.items()
        if v == Stage.INIT
    ][0]
    pre_stage_method_name = [
        k for k, v in method_to_stage.items()
        if v == Stage.PRE
    ][0]
    post_stage_method_name = [
        k for k, v in method_to_stage.items()
        if v == Stage.POST
    ][0]
    res = yield from p.extract(point_context, init_stage_method_name)
    assert res.logs == ['eulav']
    res = yield from p.extract(res, pre_stage_method_name)
    assert res.logs == ['eulav', 'value']
    res = yield from p.extract(point_context, post_stage_method_name)
    assert res.logs == ['eulav', 'value']
    res = yield from p.extract(res, 'wrong')
    assert res.logs == ['eulav', 'value']
