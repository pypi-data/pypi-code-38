#!/usr/bin/env python
# -*- coding: utf-8 -*-
# noinspection PyProtectedMember

"""Тестовые данные обработчика в виде полных схем
"""
from itertools import groupby
from operator import itemgetter

import pytest

from tracuni.define.type import (
    Rule,
    Destination,
    DestinationSection,
    Origin,
    OriginSection,
    Stage,
)


@pytest.fixture
def custom_plus_standard_schema_map(select_variants_schema_map):
    """Тестовые схемы для проверки композиции

        Генерирует две схемы одну имитирующую пользовательскую, другую
        стандартную, отличающиеся только описанием элементов: к ним
        добавляется префикс "c" или "s" соответственно. Все элементы имеют
        одинаковое назначение (<section>.NONE, 'None'), соответственно при
        композиции должен браться только первый из них. Исключение, элементы
        с индексом единица в каждой схеме (то есть вторые). В этом случае
        для пользовательской назначение меняется на (<section>.TAGS,
        'tags'), а для стандартной на (<section>.LOGS, 'logs'). Это приводит
        к тому, что первые такие должны оставаться в итоговой схеме,
        как обладающие уникальными значениями назначения.
    """
    schema_levels = ('c', 's')
    different_destinations = {
        schema_levels[0]: Destination(DestinationSection.SPAN_TAGS, 'tags'),
        schema_levels[1]: Destination(DestinationSection.SPAN_LOGS, 'logs'),
    }

    def schema_dict(schema_item):
        # noinspection PyProtectedMember
        return schema_item._asdict()

    return tuple(dict(
        (k, tuple(el[1] for el in v))
        for k, v in groupby(
            (
                (
                    variant,
                    Rule(**{
                        **schema_dict(schema_item),
                        **{
                            'description': level + schema_item.description,
                            'destination': (
                                schema_item.destination
                                if idx != 1
                                else different_destinations[level]
                            )
                        }
                    })
                )
                for variant, schema in select_variants_schema_map.items()
                for idx, schema_item in enumerate(schema)
            ),
            key=itemgetter(0)
        )
    ) for level in schema_levels)


@pytest.fixture
def mock_standard_schema(variants, point_ruleset, gen_schema_rule):
    return {
        variants[0]: point_ruleset[0],
        variants[1]: (
            gen_schema_rule(
                destination=Destination(
                    DestinationSection.REUSE,
                    'test_override',
                ),
                origins=(Origin(
                    OriginSection.POINT_ARGS,
                    lambda _: "standard",
                ),),
                pipeline=(lambda x: x[0],),
            ),
            gen_schema_rule(
                destination=Destination(
                    DestinationSection.SPAN_LOGS,
                    'test_override',
                ),
                origins=(Origin(
                    OriginSection.POINT_ARGS,
                    lambda _: "standard",
                ),),
                pipeline=(lambda x: x[0],),
            ),
        )
    }


@pytest.fixture
def auto_stage_rules(gen_schema_rule):
    return {
        Stage.INIT: (
            gen_schema_rule(
                'явно указана фаза',
                stage=Stage.INIT,
                destination=Destination(
                    section=DestinationSection.SPAN_LOGS,
                    name='a',
                ),
            ),
            gen_schema_rule(
                'нет относящих к POST, есть к INIT',
                destination=Destination(
                    section=DestinationSection.REUSE,
                    name='b',
                ),
                stage=None,
            ),
        ),
        Stage.PRE: (
            gen_schema_rule(
                'явно указана фаза',
                stage=Stage.PRE,
                destination=Destination(
                    section=DestinationSection.SPAN_LOGS,
                    name='c',
                ),
            ),
            gen_schema_rule(
                'нет ни относящих к POST, ни к INIT',
                destination=Destination(
                    section=DestinationSection.SPAN_TAGS,
                    name='d',
                ),
                origins=(
                    Origin(
                        section=OriginSection.CLIENT,
                        getter=lambda x: x
                    ),
                ),
                stage=None,
            ),
        ),
        Stage.POST: (
            gen_schema_rule(
                'явно указана фаза',
                stage=Stage.POST,
                destination=Destination(
                    section=DestinationSection.SPAN_LOGS,
                    name='e',
                ),
            ),
            gen_schema_rule(
                'есть и к POST, и к INIT',
                destination=Destination(
                    section=DestinationSection.REUSE,
                    name='f',
                ),
                origins=(
                    Origin(
                        section=OriginSection.POINT_RESULT,
                        getter=lambda x: x
                    ),
                ),
                stage=None,
            ),
            gen_schema_rule(
                'есть только к POST',
                destination=Destination(
                    section=DestinationSection.REUSE,
                    name='g',
                ),
                origins=(
                    Origin(
                        section=OriginSection.POINT_RESULT,
                        getter=lambda x: x
                    ),
                ),
                stage=None,
            ),
            gen_schema_rule(
                'Дубль назначения для проверки отбрасывания',
                destination=Destination(
                    section=DestinationSection.SPAN_LOGS,
                    name='c',
                ),
                origins=(
                    Origin(
                        section=OriginSection.POINT_RESULT,
                        getter=lambda x: x
                    ),
                ),
                stage=None,
            ),
        ),
    }
