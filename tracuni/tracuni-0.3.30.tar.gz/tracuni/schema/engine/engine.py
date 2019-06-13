#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Обработчик схем

    Управление схемами извлечения данных для различных вариантов точек

    Используется три уровня схем (в порядке убывания приоритета):
        * пользовательская на конкретную точку
            передаётся как инициализирующий параметр декоратора
        * пользовательская карта схем
            передаётся от пользователя как инициализирующий параметр
            адаптера библиотеки. Передаётся в процессор в момент его
            создания при инициализации декоратора
        * стандартная карта схем
            импортируется из schema.standard
"""

import inspect
import json

from typing import (
    TYPE_CHECKING,
    Any,
    Tuple,
    Generator,
    MutableSequence,
    Callable,
)

from tracuni.define.type import (
    Rule,
    Destination,
    DestinationSection,
    PointContext,
    PipeCommand,
    APIKind,
)
from tracuni.misc.helper import json_dumps_decode

from tracuni.schema.engine.pool import SchemaEngineCache
from tracuni.schema.engine.feed import SchemaEngineFeed
from tracuni.misc.select_coroutine import get_coroutine_decorator
async_decorator = get_coroutine_decorator()

if TYPE_CHECKING:
    from typing import List  # noqa
    from typing import Union  # noqa
    from typing import Optional  # noqa
    from tracuni.define.type import Destination  # noqa
    from tracuni.define.type import MethodNameToStage  # noqa
    from tracuni.define.type import (  # noqa
        RuleSet,
        Extractors,
    )
    from tracuni.define.type import Stage
    from tracuni.adapter import AdapterType  # noqa
    from tracuni.point.accessor import PointAccessor


SUPPRESS_BD_SPANS = False


class SchemaEngine(metaclass=SchemaEngineCache):
    """Обработчик схемы. Связь варианта со схемой извлечения данных

        * Обращается к экземпляру поставщика схем для получения списка
        применяемых правил, разбитых на фазы и дополнительных данных
        * Для заданного экземпляра объекта доступа к точке извлекает и
        возвращает данные согласно правилам и состоянию объекта доступа.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.schema_feed = None  # type: SchemaEngineFeed
        self.adapter = None  # type: AdapterType
        self.extractors = None  # type: Extractors

        self.method_to_stage = None  # type: Optional[MethodNameToStage]
        self.skip_secret_destinations = (
            None  # type: Optional[MutableSequence[Destination]]
        )
        self.secret_mask_method_name = None  # type: Optional[str]

        self._args = args
        self._kwargs = kwargs

    def observe_state_change(self, adapter: 'AdapterType'):
        """
            Обработчик схемы создаётся до того, как отработает фабрика адаптера,
            соответственно вторая часть инициализации должна проходить после
            того, как адаптер будетсоздан

        Parameters
        ----------
        adapter
            только что созданный экземпляр адаптера
        """
        self.adapter = adapter
        self._kwargs['custom_schema'] = adapter.custom_schema
        self.schema_feed = schema_feed = SchemaEngineFeed(
            *self._args,
            **self._kwargs,
        )
        self.extractors = schema_feed.parse()  # type: Extractors

        self.skip_secret_destinations = (
            schema_feed.get_skip_secret()
        )  # type: MutableSequence[Destination]

        self.secret_mask_method_name = (
            schema_feed.get_secret_mask_method_name()
        )  # type: str

    def is_tracer_disabled(self):
        return (
            self.adapter is None
            or
            (
                SUPPRESS_BD_SPANS
                and
                self.schema_feed.variant.api_kind == APIKind.DB
            )
        )

    @async_decorator
    def extract(self,
                point: 'PointAccessor',
                stage: 'Stage',
                ) -> Generator[Any, None, PointContext]:
        """Метод запускающий процесс получения и изменения исходных данных и
        данных участка для указанной точки и этапа

        Parameters
        ----------
        point
            Ссылки на данные точки и окружения с ключами, совпадающими с
            наименованиями секций источников и назначения.
        stage
            Фаза, к которой привязан обратившийся метод

        Returns
        -------
            Изменённый контекст точки
        """
        point_context = point.context
        if stage is None:
            return point_context
        extractors = (
            self.extractors.get(stage) or []
        )  # type: Union[RuleSet, List]

        for extractor in extractors:
            extracted = yield from self._extract_values(extractor, point_context)
            if extracted is None or not len(extracted):
                continue
            point_context = self._pipe_values(extractor, extracted, point)

        return point_context

###############################################################################
# Area privata

    @staticmethod
    @async_decorator
    def _extract_values(
        extractor: Rule,
        point_context: PointContext
    ) -> Generator[Any, None, Tuple[Any, ...]]:
        """

        Parameters
        ----------
        extractor
            Применяемое в данный момент правило извлечения.
        point_context
            Структура, хранящая ссылки на контекст источник данных и уже
            собранные данные. Нужна для получения контекста источника.
        Returns
        -------
            Собранные исходные значения
        """
        val = []
        # правило может содержать несколько источников
        for origin in extractor.origins:
            extracted = None

            # получаем ссылку на источник или пропускаем источник
            section_ref = getattr(
                point_context, origin.section.name.lower(), None
            )
            if section_ref is None:
                continue

            # метод извлечения, либо функция, которой передается ссылка на
            # источник, а она возвращает значение по своему разумению
            getter = origin.getter
            if callable(getter):
                is_yields = inspect.isgeneratorfunction(getter)
                if is_yields:
                    extracted = yield from getter(section_ref)
                else:
                    extracted = getter(section_ref)
            # либо метод извлечения может быть указан строкой, тогда это или
            # элемент словаря, или атрибут объекта
            elif isinstance(getter, str):
                # отдельный случай прямой слэш - возращается исходный объект
                if getter == '/':
                    extracted = section_ref
                elif isinstance(section_ref, dict):
                    extracted = section_ref.get(getter)
                else:
                    extracted = getattr(section_ref, getter, None)
            elif getter is None:
                extracted = section_ref

            # if extracted is None:
            #     continue
            val.append(extracted)

        # данные, полученные из всех указанных в правиле источников,
        # собираются в кортеж
        return tuple(val)

    def _pipe_values(self, extractor: Rule, val: Any, point: 'PointAccessor') -> PointContext:
        """Конвейер обрботки извлекаемых значений

            Вызывает цепочку методов передавая от одного к другому данные в
            текущем состоянии, обрабатывает дополнительную команду ответвления
            данных и список подавленных обработчиков.

        Parameters
        ----------
        extractor
            Правило извелечения
        val
            Данные в текущем состоянии
        point
            Структура, хранящая ссылки на контекст источник данных и уже
            собранные данные.
        Returns
        -------
            Изменённый контекст точки
        """
        tee_val = None

        for idx, process in enumerate(extractor.pipeline):
            if self._skip_secret(process, extractor.destination):
                continue

            if isinstance(process, Destination):
                if val is None:
                    continue
                destination = process  # type: Destination
                output_value = val
                if destination.section == DestinationSection.DEBUG:
                    output_value = {
                        "value": json_dumps_decode(val, indent=2),
                        "processor": process,
                        "processor_idx": idx,
                        "extractor": extractor,
                    }
                point.update_context_by_destination(destination, output_value)
                continue

            if process == PipeCommand.TEE:
                tee_val = step_back_val
                continue

            step_back_val = val
            if tee_val is not None:
                val = tee_val
            val = process(val)
            tee_val = None

        point.update_context_by_destination(extractor.destination, val)
        return point.context

    def _skip_secret(self, fn: Callable, destination: "Destination") -> bool:
        """Проверка условия пропуска обработчика маскирования по команде

        Parameters
        ----------
        fn
            Обработчик
        destination
            Описание назначения для проверки применения команды

        Returns
        -------
            Флаг надо ли запускать данный обработчик
        """
        fn_name = getattr(fn, '__name__', '')
        if self.secret_mask_method_name != fn_name:
            return False

        return (
            (
                Destination(DestinationSection.ALL, "")
                in
                self.skip_secret_destinations
            )
            or
            destination in self.skip_secret_destinations
        )
