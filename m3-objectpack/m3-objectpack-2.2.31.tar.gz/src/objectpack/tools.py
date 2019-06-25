# coding: utf-8
from __future__ import absolute_import

from collections import Mapping
from copy import deepcopy
from functools import wraps
import datetime
import types

from django.db import transaction
from django.db.models.fields import FieldDoesNotExist
from django.db.models.fields.related import RelatedField
from m3_django_compat import ModelOptions
from m3_django_compat import get_request_params
from m3_django_compat import get_related
from six.moves import map
import six


# =============================================================================
# QuerySplitter
# =============================================================================
class QuerySplitter(six.Iterator):
    """
    Порционный загрузчик выборки в итеративном контексте

    >>> from django.test.client import RequestFactory
    >>> rf = RequestFactory()
    >>> request = rf.post('', {'start': 5, 'limit': 10})
    >>> QuerySplitter.make_rows(
    ...     query=range(50),
    ...     validator=lambda x: x % 2,
    ...     request=request)
    [5, 7, 9, 11, 13, 15, 17, 19, 21, 23]
    """

    def __init__(self, query, start, limit=0):
        """
        query - выборка, start и limit - откуда и сколько отрезать.
        """
        self._data = query
        self._start = start
        self._limit = limit

        self._chunk = None
        self._cnt = 0
        self._no_more_data = False

    def __iter__(self):
        if not self._limit:
            # перекрытие метода пропускания, заглушкой
            self.skip_last = types.MethodType(lambda self: None, self)
            return iter(self._data)
        return self

    def __next__(self):
        # если уже выдали нужное кол-во, останавливаем итерацию
        if self._cnt >= self._limit:
            raise StopIteration()

        # если порция кончилась, берем следующую
        if not self._chunk and not self._no_more_data:
            self._chunk = list(
                self._data[self._start: self._start + self._limit])
            if len(self._chunk) < self._limit:
                self._no_more_data = True
            else:
                self._start += self._limit

        # отдаём порцию поэлементно
        if self._chunk:
            self._cnt += 1
            return self._chunk.pop(0)

        raise StopIteration()

    def skip_last(self):
        """
        Команда "не учитывать прошлое значение"
        """
        if not self._cnt:
            raise IndexError('Can`t skip any more!')
        self._cnt -= 1

    @classmethod
    def make_rows(
        cls, query,
        row_fabric=lambda item: item,
        validator=lambda item: True,
            request=None, start=0, limit=25):
        """
        Формирует список элементов для грида из выборки.
        Параметры листания берутся из :attr:`request`,
        или из параметров :attr:`start`/:attr:`limit`.
        Элементы перед попаданием прогоняются через :attr:`row_fabric`.
        В результирующий список попадают только те элементы,
        вызов :attr:`validator` для которых возвращает `True`

        :param query: Кварисет
        :type query: django.db.models.query.QuerySet
        :param row_fabric:
        :type row_fabric: types.FunctionType
        :param validator: Функция валидатор
        :type validator: types.FunctionType
        :param request: Реквест
        :type request: django.http.HttpRequest
        :param start: С какой записи начинать
        :type start: int
        :param limit: Сколько записей взять
        :type limit: int
        """
        if request:
            start = extract_int(request, 'start') or start
            limit = extract_int(request, 'limit') or limit

        query = cls(query, start, limit)

        rows = []
        for item in query:
            if validator(item):
                rows.append(row_fabric(item))
            else:
                query.skip_last()
        return rows


# =============================================================================
# ModelCache
# =============================================================================
class ModelCache(object):
    """
    Кэш get-ов объектов одной модели.
    В качестве ключа кэша - набор параметров для get-а
    Если в конструкторе указана фабрика объектов, то отсутствующие объекты
    создаются передачей аргументов фабрике.
    """

    def __init__(self, model, object_fabric=None):
        self._model = model
        self.MultipleObjectsReturned = model.MultipleObjectsReturned
        self._cache = {}
        self._last_kwargs = {}
        self._fabric = object_fabric

    @staticmethod
    def _key_for_dict(d):
        return tuple(sorted(six.iteritems(d), key=lambda i: i[0]))

    def _get_object(self, kwargs):
        try:
            return self._model.objects.get(**kwargs)
        except self._model.DoesNotExist:
            return None

    def get(self, **kwargs):
        self._last_kwargs = kwargs

        key = self._key_for_dict(kwargs)

        if key in self._cache:
            return self._cache[key]

        new = self._get_object(kwargs)

        if new is None and self._fabric:
            new = self._fabric(**kwargs)
            assert isinstance(new, self._model)
            assert new.id is not None

        self._cache[key] = new

        return new

    def forget_last(self):
        if self._last_kwargs:
            key = self._key_for_dict(self._last_kwargs)
            self._cache.pop(key, None)


# =============================================================================
# TransactionCM
# =============================================================================
class TransactionCM(object):
    """
    Транизакция в виде ContextManager
    """

    def __init__(self, using=None, catcher=None):
        """
        using - DB alias
        catcher - внешний обработчик исключений
        """
        self._using = using
        self._catcher = catcher or self._default_catcher

    def __enter__(self):
        transaction.enter_transaction_management(True, self._using)
        return transaction

    def __exit__(self, *args):
        result = self._catcher(*args)
        if result:
            transaction.commit(self._using)
        else:
            transaction.rollback(self._using)
        return result

    @staticmethod
    def _default_catcher(ex_type, ex_inst, traceback):
        """
        Обработчик исключений, используемый по-умолчанию
        """
        return ex_type is None


def extract_int(request, key):
    """
    Нормальный извлекатель числа

    >>> from django.test.client import RequestFactory
    >>> rf = RequestFactory()
    >>> request = rf.post('', {})
    >>> extract_int(request, 'NaN')

    >>> request = rf.post('', {'int':1})
    >>> extract_int(request, 'int')
    1
    """
    try:
        return int(get_request_params(request).get(key, ''))
    except ValueError:
        return None


def extract_int_list(request, key):
    """
    Нормальный извлекатель списка чисел

    >>> from django.test.client import RequestFactory
    >>> rf = RequestFactory()
    >>> request = rf.post('', {})
    >>> extract_int_list(request, 'list')
    []

    >>> request = rf.post('', {'list':'1,2,3,4'})
    >>> extract_int_list(request, 'list')
    [1, 2, 3, 4]
    """
    request_params = get_request_params(request)
    return list(map(
        int,
        (_f for _f in request_params.get(key, '').split(',') if _f)
    ))


def str_to_date(s):
    """
    Извлечение даты из строки

    >>> str_to_date('31.12.2012') == str_to_date('2012-12-31, Happy New Year')
    True
    """
    if s:
        s = s[:10]
        s = s.replace('-', '.')
        try:
            s = datetime.datetime.strptime(s, '%d.%m.%Y')
        except ValueError:
            try:
                s = datetime.datetime.strptime(s, '%Y.%m.%d')
            except ValueError:
                s = None
    else:
        s = None
    return s


def extract_date(request, key, as_date=False):
    """
    Извлечение даты из request`а в формате DD.MM.YYYY
    (в таком виде приходит от ExtDateField)
    и приведение к Django-формату (YYYY-MM-DD)
    """
    res = str_to_date(get_request_params(request).get(key))
    if res and as_date:
        res = res.date()
    return res


def modify(obj, **kwargs):
    """
    Массовое дополнение атрибутов для объекта с его (объекта) возвратом

    >>> class Object(object): pass
    >>> cls = Object()
    >>> cls.param1 = 0
    >>> cls = modify(cls, **{'param1':1, })
    >>> cls.param1
    1
    """
    for attr, val in six.iteritems(kwargs):
        setattr(obj, attr, val)
    return obj


def modifier(**kwargs):
    """
    Принимает атрибуты со значениями (в виде kwargs)
    Возвращает модификатор - функцию, модифицирующую передаваемый ей объект
    указанными атрибутами

    >>> w10 = modifier(width=10)
    >>> controls = map(w10, controls)
    >>> class Object(object): pass
    >>> w10 = modifier(width=10)
    >>> cls = w10(Object())
    >>> cls.width
    10

    """
    return lambda obj: modify(obj, **kwargs)


def find_element_by_type(container, cls):
    """
    Поиск экземпляров элементов во всех вложенных контейнерах

    :param container: Контейнер
    :type container: m3_ext.ui.containers.containers.ExtContainer
    :param cls: Класс
    :type cls: types.ClassType
    """
    res = []
    for item in container.items:
        if isinstance(item, cls):
            res.append(item)

        if hasattr(item, 'items'):
            res.extend(find_element_by_type(item, cls))
    return res


# =============================================================================
# collect_overlaps
# =============================================================================
def collect_overlaps(obj, queryset, attr_begin='begin', attr_end='end'):
    """
    Возвращает список объектов из указанной выборки, которые пересекаются
    с указанным объектом по указанным полям начала и конца интервала

    :param obj: Объект
    :param queryset: Выборка
    :type queryset: django.db.models.query.QuerySet
    :param attr_begin: Атрибут модели с датой начала
    :type attr_begin: str
    :param attr_end: Атрибут модели с датой конца
    :type attr_end: str
    """
    obj_bgn = getattr(obj, attr_begin, None)
    obj_end = getattr(obj, attr_end, None)

    if obj_bgn is None or obj_end is None:
        raise ValueError(
            u'Объект интервальной модели должен иметь '
            u'непустые границы интервала!')

    if obj.id:
        queryset = queryset.exclude(id=obj.id)

    result = []
    for o in queryset.iterator():
        bgn = getattr(o, attr_begin, None)
        end = getattr(o, attr_end, None)
        if bgn is None or end is None:
            raise ValueError(
                u'Среди объектов выборки присутствуют некорректные!')

        def add():
            if any((bgn <= obj_bgn <= end,
                    bgn <= obj_end <= end,
                    obj_bgn <= bgn <= obj_end,
                    obj_bgn <= end <= obj_end,)):
                result.append(o)

        try:
            add()
        except TypeError:
            if isinstance(obj_bgn, datetime.datetime) and isinstance(
                    obj_end, datetime.datetime):
                obj_bgn = obj_bgn.date()
                obj_end = obj_end.date()
                add()
    return result


# =============================================================================
# istraversable - проверка на "обходимость"
# =============================================================================
def istraversable(x):
    """
    возвращает True, если объект :attr:`x` позволяет обход себя в цикле `for`
    """
    return hasattr(x, '__iter__') or hasattr(x, '__next__') or hasattr(
        x, '__getitem__'
    )


# =============================================================================
# Кэширующий декоратор
# =============================================================================
def cached_to(attr_name):
    """
    Оборачивает простые методы (без аргументов) и property getters,
    с целью закэшировать первый полученный результат

    :param attr_name: Куда кэшировать
    :type attr_name: str
    """

    def wrapper(fn):
        @wraps(fn)
        def inner(self):
            if hasattr(self, attr_name):
                result = getattr(self, attr_name)
            else:
                result = fn(self)
                setattr(self, attr_name, result)
            return result

        return inner

    return wrapper


# =============================================================================
# парсеры для декларации контекста
# =============================================================================
def int_or_zero(s):
    """
    >>> int_or_zero('')
    0
    >>> int_or_zero('10')
    10
    """
    return 0 if not s else int(s)


def int_or_none(s):
    """
    >>> int_or_none('')
    None
    >>> int_or_none('10')
    10
    """
    return None if not s else int(s)


def int_list(s):
    """
    >>> int_list('10,20, 30')
    [10, 20, 30]
    """
    return [int(i.strip()) for i in s.split(',')]


def get_related_fields(model, fields):
    """
    >>> from django.contrib.auth.models import Permission
    >>> get_related_fields(Permission, ["content_type", "name"])
    ["content_type"]

    :param model: Django Model
    :type model: django.db.models.Model
    :param fields: Path to extract foreign object attribute
    :type fields: list
    """
    result = []
    field_name = fields.pop(0)
    if fields:
        try:
            field = ModelOptions(model).get_field(field_name)
        except (FieldDoesNotExist, KeyError, AttributeError):
            # KeyError - исключение в objectpack.ModelProxy
            # FieldDoesNotExist - в django Model
            # AttributeError - у модели может не быть меты или метода get_field
            # в случае если это VirtualModel или любая иная фейковая модель
            pass
        else:
            if isinstance(field, RelatedField):
                result.append(field_name)
                result.extend(get_related_fields(
                    get_related(field).parent_model, fields)
                )
    return result


def copy_columns(columns, *args, **kwargs):
    """Копирует параметры столбцов базового пака с одновременной модификацией.

    Предназначена для использования при расширении базовых классов паков.

    .. code-block:: python

       class BasePack:
           columns = (
               dict(
                   data_index='number',
                   width=1,
               ),
               dict(
                   data_index='code',
                   width=2,
               ),
               dict(
                   data_index='name',
                   width=4,
               ),
           )

       class Pack(BasePack)
           columns = copy_columns(
               BasePack.columns,
               dict(  # новый столбец
                   data_index='start_date',
                   width=100,
                   fixed=True,
               ),
               'code',  # место для вставки столбца code из базового класса
               dict(  # столбец name из базового класса с новыми параметрами
                   data_index='name',
                   title='Наименование',
                   width=5,
               ),
               code=dict(  # новые значения для параметров поля code
                   width=100,
               ),
           )

    :param columns: имена столбцов
    :param args: параметры новых столбцов или имена столбцов базового класса.
    :param params: новые параметры столбцов базового класса.

    :rtype: tuple or dict
    """
    assert all(isinstance(col, Mapping) for col in columns), columns

    def get_column(name):
        for column in columns:
            if column['data_index'] == name:
                result = column
                break
        else:
            result = None
        return result

    def process_arg(arg):
        if isinstance(arg, str):
            # строка с именем столбца указывает его позицию.
            column = get_column(arg)
            if column is None:
                column = dict(data_index=arg)
            else:
                column = deepcopy(column)

            if arg in kwargs:
                assert 'data_index' not in kwargs[arg], kwargs[arg]
                column.update(kwargs[arg])
            result = column

        elif isinstance(arg, Mapping):
            assert 'data_index' in arg, arg
            data_index = arg['data_index']
            column = get_column(data_index)
            if column is not None:
                column = deepcopy(column)
                column.update(arg)
                arg = column
            if data_index in kwargs:
                assert 'data_index' not in kwargs[arg], kwargs[arg]
                arg.update(kwargs[data_index])
            result = arg

        else:
            raise ValueError(arg)

        return result

    def process_kwarg(data_index, params):
        column = get_column(data_index)
        if column is None:
            result = dict(
                data_index=data_index,
                **params
            )
        elif params is True:
            result = column
        elif isinstance(params, Mapping):
            column = deepcopy(column)
            column.update(params)
            result = column
        else:
            raise ValueError((data_index, params))

        return result

    if args:
        # указаны позиционные аргументы, значит они и определяют порядок.
        return tuple(map(process_arg, args))

    else:
        return tuple(
            process_kwarg(data_index, params)
            for data_index, params in kwargs.items()
            if params is not None
        )
