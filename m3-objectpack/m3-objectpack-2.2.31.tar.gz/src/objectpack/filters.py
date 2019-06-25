# coding: utf-8
u"""Меахнизмы фильтрации справочников/реестров на базе ObjectPack."""
from __future__ import absolute_import

from functools import reduce
from operator import and_
from operator import or_
import abc
import json

from six.moves import map
import six

from django.db import models
from m3.actions import DeclarativeActionContext
from m3_django_compat import ModelOptions
from m3_django_compat import get_request_params
from m3_django_compat import get_related

from .tools import str_to_date
from .ui import _create_control_for_field


class AbstractFilterEngine(six.with_metaclass(abc.ABCMeta, object)):
    u"""
    Прототип механизма фильтрации
    """

    _config = None

    def __init__(self, columns):
        u"""
        :attr:`columns` - список вида::

            [
                (column_data_index, filter),
            ]

        где `filter` - экземпляр потомка
        :mod:`objectpack.filters.AbstractFilter`
        :param columns: Список колонок с фильтром
        :type columns: list
        """
        self._columns = dict(columns)

    @abc.abstractmethod
    def configure_grid(self, grid):
        u"""
        Метод настраивает переданный :attr:`grid` на использование фильтров

        :param grid: Грид
        :type grid: m3_ext.ui.panels.grids.ExtObjectGrid
        """
        pass

    @abc.abstractmethod
    def apply_filter(self, query, request, context):
        u"""
        :param query: Кварисет
        :type query: django.db.models.query.QuerySet
        :param request: Реквест
        :type request: django.http.HttpRequest
        :param context: Контекст
        :type context: m3.actions.context.DeclarativeActionContext
        :return: Кварисет отфильтрованный на основе параметров запроса
        :rtype: django.db.models.query.QuerySet
        """
        return query


class AbstractFilter(six.with_metaclass(abc.ABCMeta, object)):
    u"""
    Прототип класса, описывающего фильтр для потомков AbstractFilterEngine
    """

    _not = None
    _uid = None
    _lookup = None
    _default_value = None

    @property
    def default_value(self):
        if callable(self._default_value):
            return self._default_value()
        else:
            return self._default_value

    @default_value.setter
    def default_value(self, value):
        self._default_value = value

    @abc.abstractmethod
    def get_script(self):
        """
        Метод возвращает список строк-js-скриптов,
        для дополнения колонки грида
        """
        pass

    def get_q(self, params):
        """
        Метод возвращает Q-объект,
        построенный на основе данных словаря :attr:`params`

        :param params: Словарь с лукапами
        :type params: dict
        :return: Ку-объект
        :rtype: django.db.models.Q
        """
        if None in (self._uid, self._lookup):
            raise ValueError('Filter is not configured!')

        if self._uid in params:
            val = self._parser(params[self._uid])
            if callable(self._lookup):
                return self._lookup(val)
            return models.Q(**{self._lookup: val})
        else:
            return models.Q()

    def __and__(self, other):
        return FilterGroup(items=[self], op=FilterGroup.AND) & other

    def __or__(self, other):
        return FilterGroup(items=[self], op=FilterGroup.OR) | other

    def __not__(self):
        new = self.__class__(self.model, self.lookup, self.field_name)
        new._not = not self._not
        return new

    def _set_uid(self, uid_provider):
        u"""
        Проставляет uid фильтра путем вызова @uid_provider
        """
        self._uid = u'filter_%d' % uid_provider()


class FilterGroup(AbstractFilter):
    u"""
    Группа фильтров, являющихся частью булева выражения
    """
    #: И
    AND = 1
    #: Или
    OR = 2

    _items = None
    _operand = None

    def __init__(self, items, op=AND):
        """
        :param items: Фильтры
        :type items: list
        :param op: AND/OR
        :type op: int
        """
        self._items = items
        self._operand = op

    def __iter__(self):
        return iter(self._items)

    def __or__(self, other):
        return self._join(other, self.OR)

    def __and__(self, other):
        return self._join(other, self.AND)

    def __not__(self):
        return self._fork({'not': not self._not})

    def _fork(self, changes):
        assert changes, "Don`t fork the exact copy!"
        new = self.__class__(
            items=changes.get('items', self._items[:]),
            op=changes.get('op', self._operand)
        )
        new._not = changes.get('not', self._not)
        return new

    def _join(self, other, op):
        if self._operand == op:
            def wrap(x):
                return self._fork({'items': self._items + x})
        else:
            def wrap(x):
                return self.__class__(items=[self] + x, op=op)

        if isinstance(other, self.__class__):
            if self._operand == other._operand:
                if self._not == other._not:
                    # добавление списка элементов
                    return wrap(other.items)
        # Добавление единичного элемента
        return wrap([other])

    def get_script(self):
        """
        .. seealso:: :mod:`objectpack.filters.AbstractFilter.get_script`
        """
        result = []
        for item in self._items:
            result.extend(item.get_script())
        return result

    def get_q(self, params):
        """
        .. seealso:: :mod:`objectpack.filters.AbstractFilter.get_q`
        """
        if self._operand == self.OR:
            joint = or_
        else:
            joint = and_

        _q_result = reduce(joint, [i.get_q(params) for i in self._items])
        return ~_q_result if self._not else _q_result

    def _set_uid(self, auto_id_func):
        for item in self._items:
            item._set_uid(auto_id_func)


class FilterByField(AbstractFilter):
    u"""
    Фильтр на основе поля модели
    """
    #: Отображение стандартных полей модели в парсеры и лукапы
    parsers_map = [
        (models.DateField, 'date', None),
        (models.TimeField, 'time', None),
        (models.DateTimeField, 'datetime', None),
        (models.BooleanField, 'boolean', None),
        (models.FloatField, 'float', None),
        (models.DecimalField, 'decimal', None),
        ((models.IntegerField, models.ForeignKey), 'int', None),
        ((models.TextField, models.CharField), 'unicode', '%s__icontains'),
    ]

    _model = None
    _field_name = None
    _lookup = None
    _tooltip = None
    _parser = None

    def __init__(
        self, model, field_name, lookup=None, tooltip=None, default_value=None,
        **field_fabric_params
    ):
        """
        :param model: Модель, на основе поля которой и будет строиться фильтр
        :type model: django.db.models.Model
        :param filed_name: имя поля модели
        :type field_name: str
        :param lookup: либо строка-lookup для DjangoORM,
            допускающая шаблоны вида "%s__lte",
            либо функция вида (lookup_param -> Q-object)
        :param tooltip: текст всплывающей подсказки
        :type tooltip: str
        :param default_value: значение по-умолчанию
        :param field_fabric_params: Параметры для инициализации
        контрола фильтра
        :type field_fabric_params: dict

        .. note: параметр default_value может быть передан как callable объект,
                 чтобы его значение вычислялось не при инициализации пака, в
                 котором он объявлен, а только при непосредственном вызове
                 окна с гридом. Полезно, если значением по умолчанию должна
                 быть текущая дата

        .. hint: если требуется в качестве значения по-умолчанию проставить
                 значение, которое зависит от параметров запроса (выбранное в
                 виджете учреждение или дата окончания выбранного периода),
                 это можно сделать из метода create_list_window:

        .. code:

            class MyPack(ObjectPack):
                model = SomeModel

                field_filter = FilterByField(SomeModel, 'some_field')

                columns = [
                    ...,
                    {
                        ...,
                        'filter': field_filter
                    }
                ]

                def create_list_window(self, request, context):
                    some_value = get_value_by_request(request)
                    self.field_filter.default_value = some_value
                    return super(MyPack, self).create_list_window(...)
        """
        field_name = field_name.replace('.', '__')
        self._model = model
        self._field_name = field_name
        self._tooltip = tooltip
        self._field_fabric_params = field_fabric_params
        self._default_value = default_value
        for bases, parser_key, default_lookup in self.parsers_map:
            if isinstance(self.field, bases):
                self._parser = DeclarativeActionContext._parsers[parser_key]
                break
        else:
            raise TypeError('Unsupported field type: %r' % self.field)
        lookup = lookup or default_lookup
        if lookup:
            # шаблонизация лукапа, если петтерн указан
            if not callable(lookup) and '%s' in lookup:
                lookup = lookup % field_name
        else:
            def lookup(x):
                return models.Q(**{field_name: x})
        self._lookup = lookup

    def get_script(self):
        """
        .. seealso:: :mod:`objectpack.filters.AbstractFilter.get_script`
        """
        control = _create_control_for_field(
            self.field,
            **self._field_fabric_params
        )
        if 'model_register' in self._field_fabric_params:
            # в качестве настроек контрола фильтра передан
            # model_register, значит предполагается выбор из окна справочника
            # для выбора из окна справочника требуется наличие
            # actionContextJson у контрола
            control.action_context = DeclarativeActionContext()
        control._put_config_value('filterName', self._uid)
        control._put_config_value('tooltip', self._tooltip or control.label)
        control.name = self._uid
        control.allow_blank = True
        control.hide_clear_trigger = False
        control.value = self.default_value
        return [control.render()]

    @property
    def field(self):
        path = self._field_name.split('__')

        def get(model, fld, path):
            res = ModelOptions(model).get_field(fld)
            if path:
                model = get_related(res).parent_model
                return get(model, path[0], path[1:])
            return res

        res = get(self._model, path[0], path[1:])
        self.__dict__['field'] = res  # кэшируем
        return res


class CustomFilter(AbstractFilter):
    u"""
    Фильтр, строящийся на основе xtype
    """
    _xtype = None
    _parser = None
    _lookup = None
    _tooltip = None

    def __init__(self, xtype, parser, lookup, tooltip=u''):
        """
        :param xtype: xtype контрола
        :param parser: функция вида (str -> lookup_param)
        :param lookup: строка-lookup для DjangoORM,
            либо функция вида (lookup_param -> Q-object)
        :param tooltip: текст всплывающей подсказки
        """
        self._xtype = xtype
        if callable(parser):
            self._parser = parser
        else:
            self._parser = DeclarativeActionContext._parsers[parser]
        self._lookup = lookup
        self._tooltip = tooltip

    def get_script(self):
        """
        .. seealso:: :mod:`objectpack.filters.AbstractFilter.get_script`
        """
        control = [
            u'filterName: "%s"' % self._uid,
            u'xtype: "%s"' % self._xtype,
        ]
        if self._tooltip:
            control.append(u'tooltip: "%s"' % self._tooltip)
        control = u'{%s}' % u','.join(control)
        return [control]


class MenuFilterEngine(AbstractFilterEngine):
    u"""
    Механизм фильтрации, реализующий UI в виде выпадающих меню колонок
    """

    def configure_grid(self, grid):
        filter_items = []
        for k, v in six.iteritems(self._columns):
            params = {
                'type': v.get('type', 'string'),
                'data_index': k
            }
            f_options = v.get('options', [])
            if callable(f_options):
                f_options = f_options()
            params['options'] = "[%s]" % ','.join(
                (("'%s'" % item)
                 if isinstance(item, six.string_types) else
                 ((item is None and '[]') or ("['%s','%s']" % item)))
                for item in f_options)
            filter_items.append("""{
                type:'%(type)s',
                dataIndex:'%(data_index)s',
                options:%(options)s
            }""" % params)
        if filter_items:
            plugin = (
                "new Ext.ux.grid.GridFilters({filters:[%s]})" %
                ','.join(filter_items)
            )
            grid.plugins.append(plugin)

    def apply_filter(self, query, request, context):

        if hasattr(context, 'q'):
            request_filter = json.loads(context.q)

            q = models.Q()
            for item in request_filter:
                field = item[u'field']
                type_ = item[u'data'][u'type']
                value = item[u'data'][u'value']
                comp = item[u'data'].get(u'comparison')

                if type_ == u'date':
                    value = str_to_date(value)

                if not value:
                    # тут непонятно, как фильтровать:
                    # толи все записи оставить, толи ни одной
                    continue

                def make_q(field):
                    if type_ == u'list':
                        field = '%s__in' % field
                    elif type_ == u'string':
                        field = '%s__icontains' % field
                    else:
                        if comp not in (None, u'exact'):
                            field = '%s__%s' % (field, comp)
                    return models.Q(**{field: value})

                custom = self._columns[field].get('custom_field')
                if custom:
                    if callable(custom):
                        q &= custom(value)
                    else:
                        q &= reduce(or_, list(map(make_q, custom)))
                else:
                    q &= make_q(field)

            query = query.filter(q)

        return query


class ColumnFilterEngine(AbstractFilterEngine):
    u"""
    Механизм фильтрации, реализующий UI в виде полей ввода,
    встроенных в шапку таблицы
    """

    def __init__(self, columns):
        """
        .. seealso:: :mod:`objectpack.filters.AbstractFilterEngine.__init__`
        """
        self._filters = list()
        super(ColumnFilterEngine, self).__init__(columns)

        # генератор id с автоинкрементом
        def auto_id(state=[0]):
            state[0] += 1
            return state[0]

        for _, column_filter in columns:
            if isinstance(column_filter, FilterGroup):
                self._filters.extend(column_filter)
            else:
                self._filters.append(column_filter)
            column_filter._set_uid(auto_id)

    def configure_grid(self, grid):
        """
        .. seealso::
            :mod:`objectpack.filters.AbstractFilterEngine.configure_grid`
        """
        grid.plugins.append('new Ext.ux.grid.GridHeaderFilters()')
        _base_params = {}
        _new = {}
        for data_index, filter_obj in six.iteritems(self._columns):
            _new[data_index] = u'[%s]' % (u','.join(filter_obj.get_script()))

        for col in grid.columns:
            if col.data_index in _new:
                col.extra['filter'] = _new[col.data_index]

        for _filter in self._filters:
            f_value = _filter.default_value
            if f_value:
                _base_params[_filter._uid] = str(f_value)

        if _base_params:
            grid.store.base_params.update(_base_params)

    def apply_filter(self, query, request, context):
        """
        .. seealso::
            :mod:`objectpack.filters.AbstractFilterEngine.apply_filter`
        """
        q = models.Q()
        for _filter in six.itervalues(self._columns):
            q &= _filter.get_q(get_request_params(request))
        return query.filter(q)
