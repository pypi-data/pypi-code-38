#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Поставщик схем

    Разбор схем и формироавние списка правил для конкретного обработчика схем
"""

from collections import OrderedDict
from typing import (
    TYPE_CHECKING,
    Tuple,
    Optional,
    MutableSequence,
    List,
)

from tracuni.define.type import (
    Variant,
    RuleSet,
    Rule,
    SpanSide,
    APIKind,
    Schema,
    Extractors,
    Stage,
    DestinationSection,
    Destination,
    PipeCommand,
)
from tracuni.schema.standard import get_standard_schema
from tracuni.define.const import SECRET_MASK_METHOD_NAME

if TYPE_CHECKING:
    from typing import Dict  # noqa
    from typing import List  # noqa
    from typing import Sequence  # noqa
    from typing import MutableSequence  # noqa
    from tracuni.define.type import RuleSet  # noqa
    from tracuni.define.type import Schema  # noqa
    from tracuni.define.type import Destination  # noqa


class SchemaEngineFeed:
    """Подготовка схем для использования конкретным обработчиком

        * Получает ссылки на основную и пользовательские схемы и на
        определённый вариант.
        * Разбирает все схемы, выделяет из них относящиеся к заданному
        варианту и раскладывает их по фазам.
    """

    def __init__(self,
                 variant: Variant,
                 point_ruleset: Optional[RuleSet] = None,
                 custom_schema: Optional[Schema] = None,
                 ):
        self.point_ruleset = point_ruleset or tuple()
        self.custom_schema = custom_schema or {}
        self.standard_schema = get_standard_schema() or {}
        self.skip_secret_destinations = (
            []
        )  # type: MutableSequence[Destination]
        self.secret_mask_method_name = SECRET_MASK_METHOD_NAME

        self.variant = variant
        # Варианты, которые собираются из схем всех уровней в контексте
        # текущего конкретного варианта
        self.suitable_variants = OrderedDict([
            ('concrete', self.variant),
            ('all_kinds', Variant(self.variant.span_side, APIKind.ALL)),
            ('all_sides', Variant(SpanSide.ALL, self.variant.api_kind)),
            ('all_all', Variant(SpanSide.ALL, APIKind.ALL)),
        ])

    def parse(self) -> Extractors:
        """Корневая функция подготовки правил извлечения

            Объединяет все применимые для выбранного варианта наборы правил.
            Убирает неиспользуемые в силу приоритета или подавляющей
            команды. Распределяет наборы правил по этапам. Обрабатывает
            применение правил-команд для пользовательской схемы и набора
            правил точки. Для стандартной схемы их обработка не предусмотрена.

            Использует атрибуты своего объекта, ссылающиеся на
            схемы:
                * стандартную standard_schema
                * пользовательскую user_schema
                * точки point_ruleset

        Returns
        -------
            Отображение этапов извлечения на набор правил используемых на
            этом этапе.

        """
        # Выцепляем команды пропуска нижних приоритетов и маскирования из
        # набора правил точки. Если хотя бы одна комана пропуска относится
        # ко всем назначениям, то не применяем пользовательскую и стандартную
        # схемы. Делаем это отдельным первым шагом, чтобы не обрабатывать
        # схемы, если они должны быть пропущены
        custom_schema = {}  # type: Schema
        custom_ruleset = []  # type: Sequence
        standard_schema = {}  # type: Schema

        (
            point_ruleset,
            skip_below_from_point_ruleset,
            skip_dest_secret,
        ) = (
            self._should_skip_level_below(self.point_ruleset)
        )  # type: Tuple[RuleSet, List[Destination], List[Destination]]
        if not (
            Destination(DestinationSection.ALL, '')
            in
            skip_below_from_point_ruleset
        ):
            standard_schema = self.standard_schema
            custom_schema = self.custom_schema
        self.skip_secret_destinations += skip_dest_secret

        # Получаем из пользовательской схемы набор правил по текущему
        # варианту и убираем из него правила, которые должны быть
        # пропущены согласно командам, выцепленным на предыдущем шаге.
        # Выцепляем команды пропуска нижних приоритетов и маскирования из
        # пользовательской схемы. Если хотя бы одна комана пропуска относится
        # ко всем назначениям, то не применяем стандартную схему.
        if custom_schema:
            (
                custom_ruleset,
                skip_below_from_custom_schema,
                skip_dest_secret,
            ) = self._should_skip_level_below(
                self._compose_variants(
                    custom_schema,
                    skip_below_from_point_ruleset,
                )
            )
            if (
                Destination(DestinationSection.ALL, '')
                in
                skip_below_from_custom_schema
            ):
                standard_schema = {}
            self.skip_secret_destinations += skip_dest_secret

            # Получаем из стандартной схемы набор правил по текущему
            # варианту и убираем из него правила, которые должны быть
            # пропущены согласно командам, выцепленным на предыдущих шагах.
            standard_ruleset = self._compose_variants(
                standard_schema,
                (
                    skip_below_from_custom_schema
                    +
                    skip_below_from_point_ruleset
                ),
            )
        else:
            standard_ruleset = self._compose_variants(
                standard_schema,
                tuple(),
            )

        # объединяем все наборы правил из набора точки и двух схем
        collected_schema_rules = (
            *point_ruleset,
            *custom_ruleset,
            *standard_ruleset,
        )  # type: Tuple[Rule, ...]

        # раскладывем схемы по фазам и убираем из них правила, перекрытые в
        # силу приоритета
        return self._distribute_by_stages(collected_schema_rules)

    def get_skip_secret(self) -> MutableSequence[Destination]:
        return self.skip_secret_destinations or []

    def get_secret_mask_method_name(self) -> str:
        return self.secret_mask_method_name or ''

###############################################################################
# Area privata

    @staticmethod
    def _should_skip_level_below(
            schema_to_check: Optional[RuleSet] = None
    ) -> Tuple[RuleSet, List[Destination], List[Destination]]:
        """Применение пользовательской схемы поверх стандартной

        Специальной командой схемы задаётся заменяется ли стандартная
        схема пользовательской или объединяется с ней. В случае объединения
        приоритетными всё равно остаются пользовательские элементы.

        Пример элемента схемы, присутствие которого в пользовательской схеме
        отключает использование стандартной:
        (
            destination=Destination(
                section=DestinationSection.ALL,
            ),
            origins=tuple(),
            pipeline=tuple(PipeCommand.SKIP_LEVELS_BELOW,),
        )

        Parameters
        ----------
            schema_to_check

        Returns
        -------
            * Схему, из которой выброшены применённые правила
            * Список необрабатываемых назначений схем нижестоящего приоритета
            * Список необрабатываемых назначений по маскированию
        """
        if schema_to_check is None:
            schema_to_check = tuple()

        new_schema = []
        skip_dest_below = []
        skip_dest_secret = []
        for schema_rule in schema_to_check:
            skip_below_seq = tuple(
                el for el in schema_rule.pipeline
                if el == PipeCommand.SKIP_LEVELS_BELOW
            )
            if skip_below_seq:
                skip_dest_below.append(schema_rule.destination)
            skip_secret_seq = tuple(
                el for el in schema_rule.pipeline
                if el == PipeCommand.SKIP_SECRET_MASK
            )
            if skip_secret_seq:
                skip_dest_secret.append(schema_rule.destination)
            other_seq = tuple(
                el for el in schema_rule.pipeline
                if el not in (
                    PipeCommand.SKIP_LEVELS_BELOW,
                    PipeCommand.SKIP_SECRET_MASK,
                )
            )
            if len(skip_below_seq):
                if len(schema_rule.pipeline) > 1:
                    # noinspection PyProtectedMember
                    upd_rule = Rule(**{
                        **schema_rule._asdict(),
                        **{"pipeline": other_seq}
                    })
                    new_schema.append(upd_rule)
            else:
                new_schema.append(schema_rule)

        if list(
            d for d in skip_dest_below
            if d.section == DestinationSection.ALL
        ):
            skip_dest_below = [Destination(DestinationSection.ALL, ""), ]
        if list(
            d for d in skip_dest_secret
            if d.section == DestinationSection.ALL
        ):
            skip_dest_secret = [Destination(DestinationSection.ALL, ""), ]

        return (
            tuple(new_schema),
            skip_dest_below,
            skip_dest_secret,
        )

    def _compose_variants(self,
                          schema_map: Schema,
                          skip_dest: Tuple[Destination, ...],
                          ) -> RuleSet:
        """Получение набора правил для всех, подходящих к текущему,
        вариантов. Отбрасываются правила определённых назначений.

            * собираем из указанных для варианта текущего участка,
            * плюс применяемые для всех с данным направлением,
            * плюс для всех с данным протоколом,
            * плюс для всех вообще

        Parameters
        ----------
            schema_map
                входящая схема стандартная или пользовательская
            skip_dest
                список назначений, правил с которыми не применяюся из этой
                схемы

        Returns
        -------
            Единый набор правил, применимый для текущего варианта,
            полученный из данной схемы
        """
        return tuple(
            rule
            for ruleset in [
                schema_map.get(variant)
                for k, variant in self.suitable_variants.items()
            ]
            if ruleset is not None
            for rule in ruleset
            if rule.destination not in skip_dest
        )

    @staticmethod
    def _distribute_by_stages(merged: RuleSet) -> Extractors:
        """Раскладывает применяемые схемы по стадиям

            Создаётся отношение кодового имени фазы к списку применяемых
            правил. При этом гарантируется применение только первого
            встреченного правила для каждого из уникальных назначений в
            независимости от того в какую фазу оно попадает

        Parameters
        ----------
        merged
            Подготовленная схема извлечения

        Returns
        -------
            Отношение стадий к применяемым схемам
        """
        rules_to_be_applied = {}  # type: Dict[Destination, dict]

        for rule in merged:
            # пропускаем менее специфичные, чем уже зарегистрированный
            # экстрактор
            if rule.destination not in rules_to_be_applied:
                rules_to_be_applied[rule.destination] = {
                    'stage': rule.stage,
                    'extractor': rule,
                }

        # раскладываем собранные экстракторы по ключам этапов
        extractors = {}  # type: Extractors
        for stage in Stage:
            extractors[stage] = tuple(
                v['extractor']
                for k, v in rules_to_be_applied.items()
                if v['stage'] == stage
            )

        return extractors
