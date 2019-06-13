#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Привязка наборов правил к вариантам

    variant => ruleset

    ruleset = (
        Rule(
            description='',
            destination=Destination(
                section=DestinationSection.SPAN_TAGS,
                name='some'
            ),
            stage=Stage.PRE,
            origins=(
                Origin(section=OriginSection.REUSE, getter='some'),
            ),
            pipeline=(lambda x: x,),
        ),
    )  # type: RuleSet
"""
from typing import TYPE_CHECKING

from tracuni.misc.select_coroutine import is_tornado_on
from tracuni.define.type import (
    Variant,
    SpanSide,
    APIKind,
)
from tracuni.schema.builtin.tornado.ext_inner_retry_out import ruleset
from tracuni.schema.shared_rules import rule_inner_in_tracer_context, rule_inner_out_tracer_context

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from ..define.type import RuleSet  # noqa
    from ..define.type import Schema  # noqa

####################
# Подключение стандартных настроек экстракторов

# для варианта будет использован только один из наборов для определённого
# ключа назначения в зависимости от разновидности ключа экстракторы
# применяются в следующем приоритете сверху вниз (если применяется верхний,
# то нижний уже не применяется)
#  - элементы с конкретным вариантом применяются
# только для этого варианта
#  - элементы привязанные только к направлению применяются ко всем вариантам
#  с этим направлением
#  - элементы привязанные по виду API применяются ко всем вариантам с этим
#  видом
#  - непривязанные к вариантам элементы применяются ко всем вариантам


def get_standard_schema():
    from tracuni.schema.builtin import (
        inner_retry_out_ruleset,
        inner_retry_in_ruleset,
        log_out,
    )
    if is_tornado_on():
        from tracuni.schema.builtin import (
            tornado_http_in_ruleset as http_in_ruleset,
            tornado_http_out_ruleset as http_out_ruleset,
            tornado_db_out_ruleset as db_out_ruleset,
            tornado_amqp_out_ruleset as amqp_out_ruleset,
            amqp_in_ruleset,
            retry_out_ruleset,
        )
    else:
        from tracuni.schema.builtin import (
            http_in_ruleset,
            http_out_ruleset,
            amqp_in_ruleset,
            amqp_out_ruleset,
            db_out_ruleset,
            retry_out_ruleset,
        )
    standard_schema = {
        Variant(SpanSide.IN, APIKind.HTTP): http_in_ruleset,
        Variant(SpanSide.OUT, APIKind.HTTP): http_out_ruleset,
        Variant(SpanSide.IN, APIKind.AMQP): amqp_in_ruleset,
        Variant(SpanSide.OUT, APIKind.AMQP): amqp_out_ruleset,
        Variant(SpanSide.OUT, APIKind.DB): db_out_ruleset,
        Variant(SpanSide.OUT, APIKind.RETASK): retry_out_ruleset,
        Variant(SpanSide.IN, APIKind.INNER_RETRY): inner_retry_in_ruleset,
        Variant(SpanSide.OUT, APIKind.INNER_RETRY): inner_retry_out_ruleset,
        Variant(SpanSide.MID, APIKind.LOG): log_out,
        Variant(SpanSide.IN, APIKind.INNER_SHUTDOWN): log_out,
    }  # type: Schema
    return standard_schema


