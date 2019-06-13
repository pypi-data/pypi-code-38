#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Тестовые данные для внутренних структур обработчика схем
"""

import pytest

from tracuni.trac_uni import (
    Variant,
    SpanSide,
    APIKind,
    Rule,
    Destination,
    DestinationSection,
    Origin,
    OriginSection,
    StageToSections,
    Stage,
    PointContext,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tracuni.trac_uni import RuleSet  # noqa


@pytest.fixture
def variants():
    variant_sample_one = Variant(
        span_side=SpanSide.IN,
        api_kind=APIKind.HTTP,
    )
    variant_sample_two = Variant(
        span_side=SpanSide.OUT,
        api_kind=APIKind.HTTP,
    )
    variant_sample_all_all = Variant(
        span_side=SpanSide.ALL,
        api_kind=APIKind.ALL,
    )
    variant_sample_all_api_kinds = Variant(
        span_side=SpanSide.IN,
        api_kind=APIKind.ALL,
    )
    variant_sample_all_span_sides = Variant(
        span_side=SpanSide.ALL,
        api_kind=APIKind.HTTP,
    )
    return (
        variant_sample_one,
        variant_sample_two,
        variant_sample_all_all,
        variant_sample_all_api_kinds,
        variant_sample_all_span_sides,
    )


@pytest.fixture
def stage_to_sections() -> StageToSections:
    return {
        Stage.INIT: [
            DestinationSection.REUSE,
        ],
        Stage.POST: [
            OriginSection.POINT_RESULT,
        ],
    }


@pytest.fixture
def point_ruleset():
    ruleset = (
        Rule(
            description="Уцелеет только один",
            destination=Destination(
                section=DestinationSection.LOGS,
                name='None'
            ),
            origins=(Origin(
                section=OriginSection.CLIENT, getter=lambda x: x
            ),),
            pipeline=(),
        ),
        Rule(
            destination=Destination(
                section=DestinationSection.LOGS,
                name='None'
            ),
            origins=(Origin(
                section=OriginSection.CLIENT, getter=lambda x: x
            ),),
            pipeline=(),
        ),
        Rule(
            destination=Destination(
                section=DestinationSection.LOGS,
                name='None'
            ),
            origins=(Origin(
                section=OriginSection.CLIENT, getter=lambda x: x
            ),),
            pipeline=(),
        ),
        Rule(
            destination=Destination(
                section=DestinationSection.TAGS,
                name='None'
            ),
            origins=(Origin(
                section=OriginSection.CLIENT, getter=lambda x: x
            ),),
            pipeline=(),
        ),
    )  # type: RuleSet
    invalid_ruleset = ('wrong',) + ruleset
    return (
        ruleset,
        invalid_ruleset,
    )


@pytest.fixture
def gen_schema_rule():
    def fn(
        description="",
        destination=None,
        origins=None,
        pipeline=None,
        stage=Stage.INIT,
    ):
        if destination is None:
            destination = Destination(
                section=DestinationSection.LOGS,
                name='None'
            )
        if origins is None:
            origins = (
                Origin(section=OriginSection.CLIENT, getter=lambda x: x),
            )
        if pipeline is None:
            pipeline = (lambda x: x,)
        return Rule(**locals())
    return fn


@pytest.fixture
def select_variants_schema_map(gen_schema_rule, variants):
    v1, v2, v_all_all, v_all_api_kinds, v_all_span_sides, *_ = variants

    return {
        v1: (gen_schema_rule('1a'), gen_schema_rule('1b'),),
        v_all_api_kinds: (gen_schema_rule('2'),),
        v_all_span_sides: (gen_schema_rule('3a'), gen_schema_rule('3b'),),
        v_all_all: (gen_schema_rule('4'),),
        v2: (gen_schema_rule('5a'), gen_schema_rule('5b'),),
    }


@pytest.fixture
def point_context():
    class Data:
        some = "value"

    def fn(x):
        return x

    res = PointContext(
        point_args={"some": "value"},
        point_ref=fn,
        adapter=object(),
        engine=object(),
        reuse={"some": "value"},
        span=Data(),
        logs=[],
        tags={},
        span_id={},
    )
    return res
