# coding: utf-8
"""
Виртуальная модель и proxy-обертка для работы с группой моделей
"""
from __future__ import absolute_import

from collections import Iterable
from functools import reduce
from itertools import islice
import copy

from six.moves import filter
from six.moves import filterfalse
from six.moves import map
from six.moves import zip
import six

from django.db.models import manager
from django.db.models import query
from m3_django_compat import ModelOptions
from m3_django_compat import get_related


def kwargs_only(*keys):
    keys = set(keys)

    def wrapper(fn):
        def inner(self, *args, **kwargs):
            wrong_keys = set(kwargs.keys()) - keys
            if wrong_keys:
                raise TypeError(
                    '%s is an invalid keyword argument(s)'
                    ' for this function' % (
                        ', '.join('"%s"' % k for k in wrong_keys)))
            return fn(self, args, **kwargs)

        return inner

    return wrapper


def _call_if_need(x):
    return x() if callable(x) else x


# ==============================================================================
# VirtualModelManager
# =============================================================================


class ObjectWrapper(object):

    """Обертка над объектами, инвертирующая результат сравнения больше/меньше.

    Используется для сортировки данных в виртуальных моделях.
    """

    def __init__(self, obj, direction):
        self.obj = obj
        self.direction = direction

    def __eq__(self, other):
        if isinstance(other, ObjectWrapper):
            other = other.obj
        return self.obj == other

    def __lt__(self, other):
        if isinstance(other, ObjectWrapper):
            other = other.obj

        is_obj_not_none = self.obj is not None
        is_other_not_none = other is not None
        if is_obj_not_none and is_other_not_none:
            first, second = self.obj, other
        else:
            first, second = is_obj_not_none, is_other_not_none

        return first < second if self.direction == 1 else first > second


class VirtualModelManager(object):
    """
    Имитация QueryManager`а Django для VirtualModel.
    """
    _operators = {
        'contains': lambda val: lambda x: val in x,
        'iexact': lambda val: lambda x, y=val.lower(): x.lower() == y,
        'icontains': lambda val: lambda x, y=val.lower(): y in x.lower(),
        'lte': lambda val: lambda x: x <= val,
        'gte': lambda val: lambda x: x >= val,
        'lt': lambda val: lambda x: x < val,
        'gt': lambda val: lambda x: x > val,
        'isnull': lambda val: lambda x: (x is None or x.id is None) == val,
        'in': lambda vals: lambda x: x in vals,
        'overlap': lambda vals: (
            lambda searched_vals: set(searched_vals) & set(vals)
        ),
    }

    def __init__(self, model_clz=None, procs=None, **kwargs):
        if not model_clz:
            return
        self._clz = model_clz
        self._procs = procs or []
        self._ids_getter_kwargs = kwargs

    def __get__(self, inst, clz):
        if inst:
            raise TypeError("Manager can not be accessed from model instance!")
        return self.__class__(clz)

    def all(self):
        return self._fork_with(self._procs[:])

    def __getitem__(self, arg):
        if isinstance(arg, slice):
            procs = self._procs[:]
            procs.append(
                lambda data: islice(data, arg.start, arg.stop, arg.step))
            return self._fork_with(procs)
        return list(self)[arg]

    def __iter__(self):
        return reduce(
            lambda arg, fn: fn(arg),
            self._procs,
            map(
                self._clz._from_id,
                _call_if_need(
                    self._clz._get_ids(
                        **self._ids_getter_kwargs))))

    def _fork_with(self, procs=None, **kwargs):
        kw = self._ids_getter_kwargs.copy()
        kw.update(kwargs)
        if not procs:
            procs = self._procs[:]
        return self.__class__(self._clz, procs, **kw)

    def configure(self, **kwargs):
        return self._fork_with(**kwargs)

    @classmethod
    def _make_getter(cls, key, val=None, allow_op=False):
        def folder(fn, attr):
            return lambda obj: fn(getattr(obj, attr))

        def default_op(op):
            return lambda val: lambda obj: val == getattr(obj, op)

        key = key.split('__')
        if allow_op:
            if len(key) > 1:
                op = key.pop()
                op = cls._operators.get(op, default_op(op))(val)
            else:
                op = (lambda val: lambda obj: obj == val)(val)
        else:
            def op(obj):
                return obj
        return reduce(folder, reversed(key), op)

    @classmethod
    def _from_q(cls, q):
        fns = [
            cls._make_getter(c[0], c[1], allow_op=True)
            if isinstance(c, tuple) else
            cls._from_q(c)
            for c in q.children
        ]
        comb = all if q.connector == q.AND else any
        return lambda obj: comb(f(obj) for f in fns)

    def _filter(self, combinator, args, kwargs):
        procs = self._procs[:]
        fns = []
        if args:
            fns.extend(self._from_q(q) for q in args)
        if kwargs:
            fns.extend(
                self._make_getter(key, val, allow_op=True)
                for key, val in six.iteritems(kwargs)
            )
        if fns:
            procs.append(
                lambda items: combinator(
                    lambda obj: all(fn(obj) for fn in fns), items))
        return self._fork_with(procs)

    def filter(self, *args, **kwargs):
        return self._filter(filter, args, kwargs)

    def exclude(self, *args, **kwargs):
        return self._filter(filterfalse, args, kwargs)

    def order_by(self, *args):
        procs = self._procs[:]

        getters, dirs = [], []
        for a in args:
            if a.startswith('-'):
                d = -1
                a = a[1:]
            else:
                d = 1
            getters.append(self._make_getter(a))
            dirs.append(d)

        if getters:
            # генератор процедур сортировки
            def make_proc(**kwargs):
                return lambda data: iter(sorted(data, **kwargs))

            def key_fn(obj):
                return tuple(
                    ObjectWrapper(getter(obj), direction)
                    for getter, direction in zip(getters, dirs)
                )

            procs.append(make_proc(key=key_fn))

        return self._fork_with(procs)

    def get(self, *args, **kwargs):
        if args and not kwargs:
            kwargs['id'] = args[0]
        result = list(self.filter(**kwargs))
        if not result:
            raise self._clz.DoesNotExist()
        elif len(result) > 1:
            raise self._clz.MultipleObjectsReturned()
        return result[0]

    def values(self, *args):
        return (
            dict(list(zip(args, t)))
            for t in self.values_list(*args)
        )

    @kwargs_only('flat')
    def values_list(self, args, flat=False):
        if flat and len(args) > 1:
            raise TypeError(
                "'flat' is not valid when values_list is "
                "called with more than one field"
            )
        if flat:
            getter = self._make_getter(args[0])
            return map(getter, self)
        else:
            getters = list(map(self._make_getter, args))
            return (tuple(g(o) for g in getters) for o in self)

    def select_related(self):
        return self

    def count(self):
        return sum(1 for _ in self)

    def __len__(self):
        return self.count()


# =============================================================================
# VirtualModel
# =============================================================================
class VirtualModel(object):
    """
    Виртуальная модель, реализующая Django-ORM-совместимый API, для
    работы с произвольными данными.

    Менеджер поддерживает дополнительный лукап:
      - overlap: для проверки пересечения iterable-поля объекта виртуальной
            модели и передаваемого iterable-объекта.

    Пример модели:
    >>> M = VirtualModel.from_data(
    ...     lambda: (
    ...         {'x': x, 'y': y * 10}
    ...         for x in xrange(5)
    ...         for y in xrange(5)
    ...     ),
    ...     auto_ids=True
    ... )

    Теперь с моделью можно работать так:
    >>> M.objects.count()
    25
    >>> M.objects.filter(x__gte=2).exclude(y__in=[10, 20, 30]).count()
    6
    >>> list(M.objects.filter(x=0).order_by("-y").values_list("y", flat=True))
    [40, 30, 20, 10, 0]

    Пример фильтрации по ``overlap``:

    >>> M = VirtualModel.from_data(
    ...     lambda: (
    ...         {'related_objects_values': [x, y * 10], 'y': y * 10}
    ...         for x in range(3)
    ...         for y in range(3)
    ...     ),
    ...     auto_ids=True
    ... )

    Найти все объекты, у которых в ``related_objects_values``
    пересекается c [2, 20].
    >>> list(M.objects.filter(
    ...     related_objects_values__overlap=[2, 20]
    ... ).values('related_objects_values'))
    [{'related_objects_values': [0, 20]},
     {'related_objects_values': [1, 20]},
     {'related_objects_values': [2, 0]},
     {'related_objects_values': [2, 10]},
     {'related_objects_values': [2, 20]}]

    """

    class DoesNotExist(Exception):
        pass

    class MultipleObjectsReturned(Exception):
        pass

    @classmethod
    def _get_ids(cls):
        """
        Метод возвращает iterable, или callable, возвращаюший iterable,
        для каждого элемента которого (iterable)
        будет инстанцирован объект класса
        (каждый эл-т итератора передаётся в конструктор)
        """
        return NotImplemented

    @classmethod
    def _from_id(cls, data):
        return cls(data)

    objects = VirtualModelManager()

    @classmethod
    def from_data(cls, data, auto_ids=False, class_name="NewVirtualModel"):
        """
        Возвращает субкласс, основанный на переданных данных
        @data - iterable из словарей
        @auto_ids - если True, поле id объектов модели
                    будет генерироваться автоматически
        @class_name - имя класса-потомка
        """
        if auto_ids:
            def get_ids(cls):
                cnt = 1
                for d in _call_if_need(data):
                    d['id'] = cnt
                    yield d
                    cnt += 1
        else:
            def get_ids(cls):
                return data

        return type(
            class_name,
            (cls,),
            {
                '_get_ids': classmethod(get_ids),
                '__init__': lambda self, data: self.__dict__.update(data),
                '__repr__': lambda self: '%s(%r)' % (
                    self.__class__.__name__,
                    self.__dict__)
            }
        )


# =============================================================================
# model_proxy_metaclass
# =============================================================================
class ModelProxyMeta(type):
    """
    Метакласс для ModelProxy
    """

    def __new__(cls, name, bases, dic):
        model = dic.get('model')
        relations = dic.get('relations') or []

        if not model:
            return type(name, bases, dic)

        class LazyMetaData(object):
            """
            Дескриптор, реализующий ленивое построение данных,
            необходимых для работы meta-данных прокси-модели
            """
            FIELDS, FIELD_DICT = 0, 1

            _CACHING_ATTR = '_lazy_metadata'

            def __init__(self, attr):
                self._attr = attr

            def __get__(self, inst, clazz):
                # дескриптор должен работать только для класса
                assert inst is None
                cache = getattr(clazz, self._CACHING_ATTR, None)
                if not cache:
                    cache = self._collect_metadata()
                    setattr(clazz, self._CACHING_ATTR, cache)
                return cache[self._attr]

            def _collect_metadata(self):
                # сбор полей основной модели и указанных моделей,
                # связанных с ней
                def add_prefix(field, prefix):
                    field = copy.copy(field)
                    field.attname = '%s.%s' % (prefix, field.attname)
                    return field

                def submeta(meta, path):
                    for field in path.split('.'):
                        field = ModelOptions(meta.model).get_field(field)
                        meta = get_related(field).parent_model._meta
                    return meta

                meta = model._meta
                fields_ = []
                fields_dict = {}
                for prefix, meta in [(model.__name__.lower(), meta)] + [
                        (rel, submeta(meta, rel)) for rel in relations]:
                    for f in meta.fields:
                        f = add_prefix(f, prefix)
                        fields_.append(f)
                        fields_dict[f.attname] = f

                return fields_, fields_dict

        # django-подобный класс метаинформации о модели
        class BaseMeta(object):
            fields = LazyMetaData(LazyMetaData.FIELDS)
            field_dict = LazyMetaData(LazyMetaData.FIELD_DICT)

            verbose_name = model._meta.verbose_name
            verbose_name_plural = model._meta.verbose_name_plural

            @classmethod
            def get_field(cls, field_name):
                return cls.field_dict[field_name]

        meta_mixin = dic.pop('Meta', None)
        if meta_mixin:
            dic['_meta'] = type('_meta', (meta_mixin, BaseMeta), {})
        else:
            dic['_meta'] = BaseMeta

        relations_for_select = [r.replace('.', '__') for r in relations]

        # обёртка над QueryManager
        class WrappingManager(object):

            def __init__(self, manager, proxy=None):
                self._manager = manager
                self._proxy_cls = proxy
                self._query = None

            def _get_query(self):
                if not self._query:
                    try:
                        self._query = self._manager._clone()
                    except AttributeError:
                        self._query = self._manager
                return self._query.select_related(*relations_for_select)

            def __get__(self, inst, clz):
                if inst:
                    raise TypeError(
                        "Manager can not be accessed from model instance!")
                return self.__class__(self._manager, clz)

            def __iter__(self):
                # при итерации по объектам выборки основной модели,
                # каждый объект оборачивается в Proxy
                for item in self._get_query():
                    yield self._proxy_cls(item)

            def get(self, *args, **kwargs):
                return self._proxy_cls(self._get_query().get(*args, **kwargs))

            def iterator(self):
                return iter(self)

            def __getitem__(self, *args):
                def wrap(obj):
                    if isinstance(obj, (list, dict)):
                        return obj
                    return self._proxy_cls(obj)

                result = self._get_query().__getitem__(*args)

                if isinstance(result, Iterable):
                    return map(wrap, result)
                else:
                    return wrap(result)

            def __getattr__(self, attr):
                # все атрибуты, которые не перекрыты,
                # берутся в Manager`е базовой модели
                if attr in self.__dict__:
                    return self.__dict__[attr]
                else:
                    result = getattr(self._manager, attr)

                    def wrapped(fn):
                        def inner(*args, **kwargs):
                            result = fn(*args, **kwargs)
                            if isinstance(
                                    result, (manager.Manager, query.QuerySet)):
                                return self.__class__(result, self._proxy_cls)
                            return result

                        return inner

                    if callable(result):
                        return wrapped(result)
                    return result

        dic['objects'] = WrappingManager(model.objects)

        dic['DoesNotExist'] = model.DoesNotExist
        dic['MultipleObjectsReturned'] = model.MultipleObjectsReturned

        # создание класса Proxy
        return super(ModelProxyMeta, cls).__new__(cls, name, bases, dic)


model_proxy_metaclass = ModelProxyMeta


# =============================================================================
# ModelProxy
# =============================================================================
class ModelProxy(six.with_metaclass(model_proxy_metaclass, object)):
    """
    Proxy-объект инкапсулирующий в себе несколько моделей
    (для случая, когда одна модель - основная, о другие - её поля)
    """

    model = None

    # список извлекаемых связанных моделей вида
    # ['relation', 'relation2.relation3']
    relations = None

    def __init__(self, obj=None):
        self.relations = self.relations or []
        if obj is None:
            def wrap_save_method(child, parent, attr):
                old_save = child.save

                def inner(*args, **kwargs):
                    result = old_save(*args, **kwargs)
                    setattr(parent, attr, child.id)
                    return result

                return inner

            # если объект не указан - создается новый
            obj = self.model()
            # список объектов, созданных при заполнении связанных объектов
            created_objects = []
            # создаются экземпляры связанных объектов (вглубь)
            for path in self.relations:
                sub_obj, sub_model = obj, self.model
                for item in path.split('.'):
                    # получение связанной модели
                    field = ModelOptions(sub_model).get_field(item)
                    sub_model = get_related(field).parent_model
                    # объект может быть уже заполнен, при частично
                    # пересекающихся путях в relations
                    # в этом случае новый объект не создается,
                    # а испольуется созданный ранее
                    try:
                        existed = getattr(sub_obj, item, None)
                    except sub_model.DoesNotExist:
                        existed = None
                    if existed and existed in created_objects:
                        sub_obj = existed
                        continue
                    # создание пустого объекта
                    new_sub_obj = sub_model()
                    created_objects.append(new_sub_obj)
                    # оборачивание save, для простановки xxx_id у род.модели
                    new_sub_obj.save = wrap_save_method(
                        new_sub_obj, sub_obj, '%s_id' % item)
                    # созданный объект, вкладывается в зависимый
                    setattr(sub_obj, item, new_sub_obj)
                    # подъем на уровень выше
                    sub_obj = new_sub_obj
            self.id = None
        else:
            self.id = obj.id

        setattr(self, self.model.__name__.lower(), obj)
        setattr(self, '_object', obj)
        # заполнение атрибутов proxy по заданным связям вглубь (xxx.yyy)
        for rel in self.relations:
            attr = rel.split('.', 1)[0]
            setattr(self, attr, getattr(obj, attr, None))

    def save(self):
        raise NotImplementedError()

    def safe_delete(self):
        raise NotImplementedError()
