#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Переиспользование экземпляров механизма извлечения

    Для каждого используемого варианта экземпляр создаётся один раз.
    Исключение составляет случай, когда передаётся набор правил точки,
    для упрощения, чтобы не надо было проверять одинаковые это
    пользовательские правила для точки или нет.
"""

from typing import (
    TYPE_CHECKING,
    Any,
    Tuple,
)

from ...define.type import (
    Variant,
    RuleSet,
    Rule,
    Schema,
)
from ...define import errors as err

if TYPE_CHECKING:
    from typing import Dict  # noqa
    from typing import Optional  # noqa


class SchemaEngineCache(type):
    """Сохранение экземпляров мастера схем для переиспользования

        Не сохраняет, если задана пользовательская схема
    """

    def __init__(cls, *args: Any, **kwargs: Any):
        """Перекрывается для создания атрибута хранения кеша
        """
        super().__init__(*args, **kwargs)
        cls._cache = {}  # type: Dict[Variant, Any]

    def __call__(
        cls: 'SchemaEngineCache',
        *args: Any,
        **kwargs: Any
    ) -> 'SchemaEngineCache':
        """Перекрывается для работы с кешем при создании процессора

            * получает инициализирующие параметры и проверяет их
            * берет экземпляр процессора из кеша, если нет пользовательской
            схемы, а он там есть
            * создаёт экземпляр
            * записывает  созданный экземпляр в кеш, если нет
            пользовательской схемы

        Parameters
        ----------
        variant (или нулевой в позиционных аргументах)
            используется как ключ кеша для созданного экземпляра
        custom_schema (или первый в позиционных аргументах)
            проверяется наличие, чтобы не создавать кеш для процессора с
            пользовательской схемой

        Returns
        -------
            Созданный экземпляр процессора
        """
        self = None  # type: Optional[SchemaEngineCache]

        variant, point_ruleset, _ = cls._provide_init_values(
            args, kwargs
        )

        if point_ruleset is None:
            self = cls._cache.get(variant)
        if self is None:
            self = super().__call__(*args, **kwargs)
            if point_ruleset is None:
                cls._cache[variant] = self

        return self

    def _provide_init_values(
        self,
        args: Any, kwargs: Any
    ) -> Tuple[Variant, RuleSet, Schema]:
        """Обработка параметров инициализации конкретного объекта

            Получает параметры варианта или пользовательской схемы из
            позиционных или именованных аргументов экземпляра дочернего
            объекта.

        Parameters
        ----------
        variant (или нулевой в позиционных аргументах)
            используется как ключ кеша для созданного экземпляра
        custom_schema (или первый в позиционных аргументах)
            проверяется наличие, чтобы не создавать кеш для процессора с
            пользовательской схемой
        custom_schema_map (или второй в позиционных аргументах)
            на уровне мета-класса только проверяется

        Returns
        -------
            Возвращает кортеж из полученных параметров
        """
        variant = (args[0:1] or [None])[0]  # type: Optional[Variant]
        if variant is None:
            variant = kwargs.get('variant')
        point_ruleset = (args[1:2] or [None])[0]  # type: Optional[RuleSet]
        if point_ruleset is None:
            point_ruleset = kwargs.get('point_ruleset')
        custom_schema = (
            args[2:3] or [None]
        )[0]  # type: Optional[Schema]
        if custom_schema is None:
            custom_schema = kwargs.get('custom_schema')

        return self._check_arguments(variant, point_ruleset, custom_schema)

    @staticmethod
    def _check_arguments(
        variant: Variant,
        point_ruleset: RuleSet,
        custom_schema: Schema,
    ) -> Tuple[Variant, RuleSet, Schema]:
        """Проверяет инициализирующие аргументы

        Parameters
        ----------
        variant
            Проверяемый аргумент, должен присутствовать
        point_ruleset
        custom_schema
            Проверяемый аргумент, необязателен

        Returns
        -------
            Те же аргументы, что и на входе

        Raises
        -------
            Ошибку проверки наличия или типа того или иного аргумента
        """
        if not isinstance(variant, Variant):
            raise err.ProcessorInitNoneOrWrongTypeVariant

        if (
            point_ruleset
            and
            (
                not isinstance(point_ruleset, tuple)
                or
                any(type(el) != Rule for el in point_ruleset)
            )
        ):
            raise err.ProcessorInitWrongTypeCustomSchema

        if (
            custom_schema
            and
            (
                not isinstance(custom_schema, dict)
                or
                any(type(el) != Variant for el in custom_schema.keys())
                or
                any(
                    type(schema_item) != Rule
                    for schema in custom_schema.values()
                    for schema_item in schema
                )
            )
        ):
            raise err.ProcessorInitWrongTypeCustomSchema

        return variant, point_ruleset, custom_schema
