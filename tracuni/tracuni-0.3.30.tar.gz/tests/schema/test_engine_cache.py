#!/usr/bin/env python
# -*- coding: utf-8 -*-
# noinspection PyProtectedMember

"""Проверка кеширования обработчиков схем
"""

import pytest

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from tracuni.trac_uni import (
        SchemaEngineCache,
    )  # noqa


# pytest.skip('skipping {} tests'.format(__name__), allow_module_level=True)


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test_proc_cache_init(
    engine_types,
    variants,
):
    e_c_t = engine_types[1]  # type: SchemaEngineCache
    err = engine_types[3]
    test_variant, test_another_variant, *_ = variants

    class Processor(metaclass=e_c_t):
        def __init__(self, *args, **kwargs):
            pass

    with pytest.raises(
        err.ProcessorInitNoneOrWrongTypeVariant,
    ) as exc_info:
        invalid_processor = Processor()
        del invalid_processor
    assert (
        exc_info
    ), "Нельзя создать процессор без варианта"

    with pytest.raises(
        err.ProcessorInitNoneOrWrongTypeVariant,
    ) as exc_info:
        invalid_processor = Processor('wrong')
        del invalid_processor
    assert (
        exc_info
    ), "Нельзя создать процессор с неправильным вариантом"

    processor = Processor(
        test_variant,
    )
    assert (
        processor
    ), "Можно создать процессор без пользовательских схем"

    processor_cache = getattr(processor, '_cache', None)
    assert (
        isinstance(processor_cache, dict)
    ), "Содержит словарный атрибут кеша"
    assert (
        processor_cache
    ), "Кешируется, если нет пользовательской схемы"

    processor_the_same_variant = Processor(
        test_variant,
    )
    assert (
        processor_the_same_variant._cache is processor._cache
    ), "Кеш един для обоих экземпляров"
    assert (
        len(processor_cache) == 1
    ), "Не создаётся новая запись в кеше для того же варианта"

    Processor(
        test_another_variant,
    )
    assert (
        len(processor_cache) == 2
    ), "Создаётся новая запись в кеше для другого варианта"


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test_proc_cache_init_cust_point(
    engine_types,
    point_ruleset,
    variants,
):
    (
        _,
        e_c_t,  # type: SchemaEngineCache
        _,
        err,
    ) = engine_types
    ruleset, invalid_ruleset, *_ = point_ruleset
    test_variant, *_ = variants

    class Processor(metaclass=e_c_t):
        def __init__(self, *args, **kwargs):
            pass

    processor = Processor(
        test_variant,
        ruleset,
    )

    processor_cache = getattr(processor, '_cache', None)
    assert (
        isinstance(processor_cache, dict)
    ), "Содержит словарный атрибут кеша"
    assert (
        not processor_cache
    ), "Не кешируется, если инициализируется с пользовательской схемой точки"

    with pytest.raises(
        err.ProcessorInitWrongTypeCustomSchema,
    ) as exc_info:
        invalid_processor = Processor(
            test_variant,
            'wrong'
        )
        del invalid_processor
    assert (
        exc_info
    ), "Отлавливается ошибка, когда схема полностью некорректна"

    with pytest.raises(
        err.ProcessorInitWrongTypeCustomSchema,
    ) as exc_info:
        invalid_processor = Processor(
            test_variant,
            invalid_ruleset,
        )
        del invalid_processor
    assert (
        exc_info
    ), "Отлавливается ошибка, когда один из элементов схемы некорректен"


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test_proc_cache_init_cust_map(
    engine_types,
    point_ruleset,
    variants,
):
    _, e_c_t, _, err = engine_types
    ruleset, invalid_ruleset, *_ = point_ruleset
    test_variant, *_ = variants

    class Processor(metaclass=e_c_t):
        def __init__(self, *args, **kwargs):
            pass

    processor = Processor(
        test_variant,
        custom_schema={
            test_variant: ruleset
        }
    )

    processor_cache = getattr(processor, '_cache', None)
    assert (
        isinstance(processor_cache, dict)
    ), "Содержит словарный атрибут кеша"
    assert (
        processor_cache
    ), "Кешируется, если инициализируется с пользовательской картой схем"

    with pytest.raises(
        err.ProcessorInitWrongTypeCustomSchema,
    ) as exc_info:
        invalid_processor = Processor(
            test_variant,
            custom_schema='wrong'
        )
        del invalid_processor
    assert (
        exc_info
    ), "Отлавливается ошибка, когда карта полностью некорректна"

    with pytest.raises(
        err.ProcessorInitWrongTypeCustomSchema,
    ) as exc_info:
        invalid_processor = Processor(
            test_variant,
            custom_schema={
                test_variant: invalid_ruleset
            }
        )
        del invalid_processor
    assert (
        exc_info
    ), "Отлавливается ошибка, когда один из элементов карты "
    "содержит некорректную схему"

    with pytest.raises(
        err.ProcessorInitWrongTypeCustomSchema,
    ) as exc_info:
        invalid_processor = Processor(
            test_variant,
            custom_schema={
                'wrong': ruleset
            }
        )
        del invalid_processor
    assert (
        exc_info
    ), "Отлавливается ошибка, когда один из элементов карты "
    "содержит некорректный ключ-вариант"


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test_engine_inst_cache(
    engine_types,
    variants
):
    engine_t = engine_types[0]
    e = engine_t(variants[0])
    another_e_same_variant = engine_t(variants[0])
    third_e_other_variant = engine_t(variants[1])
    assert e is another_e_same_variant
    assert another_e_same_variant is not third_e_other_variant
    assert e is not third_e_other_variant
