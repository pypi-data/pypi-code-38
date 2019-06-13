# encoding: utf-8
from __future__ import unicode_literals

import uuid
import collections

from django.db import models
from rest_framework.pagination import BasePagination

import coreapi


def _get_serializer_name(serializer_class=None, model=None):
    if model:
        obj_name = model._meta.object_name.lower()
    elif "Serializer" in serializer_class.__name__:
        obj_name = serializer_class.__name__.split("Serializer")[0].lower()
    else:
        obj_name = serializer_class.__name__.lower()
    return obj_name


def _get_fields(serializer_class=None, model=None):
    if model:
        return model._meta.get_fields()
    if not hasattr(serializer_class, "Meta"):
        return []
    return serializer_class.Meta.model._meta.get_fields()


class Serializer(object):
    def __init__(self, serializer_class=None, model=None):
        """初始化，serializer_class和model中可能 只会传其中一个

        :serializer_class: drf中的serializer_class类
        :model: Model类
        :returns: None

        """
        self.serializer_class = serializer_class
        self.name = _get_serializer_name(serializer_class=serializer_class, model=model)
        #  try:
        #  self.model = serializer_class.Meta.model
        #  except:
        self.fields = _get_fields(serializer_class=serializer_class, model=model)

    def getDefaultValue(self):
        """根据Model获取初始化值，首先取model中的第一行数据，
        如果该model对应表中无数据，则实例化一个空Model类

        :returns: dict

        """
        isntance = model.objects.first()
        if not instance:
            instance = model()
        try:
            data = self.serializer(instance).data
        except Exception:
            print_exc()
            data = {}
        return data


class Result(object):
    def __init__(self, dataset=None, serializer=None, paginator=None):
        """
        :dataset: 返回的结果集, list,dict 不可以为迭代器
        :serializer_class: ViewSet或View中定义的序列化类
        :paginator: 分页方法
        """
        self.errors = []
        self.serializer = serializer
        self.dataset = None
        self.msg = None
        self.code = 200
        self.paginator = paginator

    def data(self, dataset):
        self.dataset = dataset
        return self

    def error(self, key: str, value: str, **kwargs):
        """
        把错误信息存储在self.errors
        :key: str 错误信息的key，如name
        :value: str 错误信息的值
        :return: self
        """
        self.errors.append((key, value))
        return self

    def status(self, code: int, msg: str=''):
        """
        设置状态码，在__call__方法中根据self._code转为具体的API格式
        :code: http状态码
        msg: 该状态的消息体
        """
        self.code = code
        if msg:
            self._message = msg
        return self

    def response(self, data, status=None):
        """
        子类实现
        """

    def __call__(
        self, status: int = 0, serialize: bool = False, paging: bool = True, **kwargs
    ):
        """
        :status: 返回的状态码
        :serialize: bool 是否根绝self.serializer_class 对data做序列化
        :paging: 是否根据self.paginator 对dataset进行分页
        """
        serialize = self.serializer and serialize
        if status:
            self.code = status
        dataset = self.dataset
        if serialize:
            if isinstance(data, Model):
                data = self.serializer(dataset).data
            elif isinstance(dataset, collections.abc.Iterable) and not isinstance(dataset, dict) and dataset and isinstance(dataset[0], Model):
                # list 方法返回可迭代对象, dataset可以为迭代器
                data = self.serializer(dataset, many=True).data
                return self.paginator.paginate_queryset(data, self.paginator.request)
        else:
            data = dataset
        return self.response(data, self.code)

    def __bool__(self):
        return 200 <= self.code < 400

    __nonzero__ = __bool__


def getPageParams(request, keys):
    page = str(request.GET.get("page", 1))
    page = int(page.isdigit() and page or 1)
    pagesize = str(request.GET.get("pagesize", 10))
    split = pagesize.isdigit()
    pagesize = min(int(pagesize.isdigit() and pagesize or 10), 100)
    iTotalRecords = len(keys)
    startRecord = (page - 1) * pagesize
    endRecord = (
        iTotalRecords
        if iTotalRecords - startRecord < pagesize
        else startRecord + pagesize
    )

    return startRecord, endRecord, pagesize, iTotalRecords, split


class PageNumberPager(BasePagination):
    page_query_param = "page"
    page_size_query_param = "pagesize"

    def paginate_queryset(self, keys, request, **kwargs):
        """

        :param keys:
        :param request:
        :param kwargs:
        :return:
        """
        result = {"code": "200000", "page": {"current": 0, "pagesize": 10, "total": 0}}

        start, end, pagesize, iTotalRecords, split = getPageParams(request, keys)
        if not isinstance(keys, list):  # py3兼容 dict_values不是list
            keys = list(keys)

        if split:
            keys = keys[start:end]
        else:
            pagesize = iTotalRecords

        result["page"]["current"] = start
        result["page"]["total"] = iTotalRecords
        result["page"]["pagesize"] = pagesize
        result["items"] = keys
        return result

    def get_schema_fields(self, view):
        fields = [
            coreapi.Field(
                name=self.page_query_param,
                required=False,
                location="query",
                description="分页参数：当为空时，获取全量数据",
                type="integer",
            )
        ]
        if self.page_size_query_param is not None:
            fields.append(
                coreapi.Field(
                    name=self.page_size_query_param,
                    required=False,
                    location="query",
                    description="分页参数：当为空时，获取全量数据，当传值时，支持[10, 25, 50, 100]分页",
                    type="integer",
                )
            )
        return fields


class Valid(object):
    def __init__(self, method, **kwargs):
        """
        status 是一个属性，而不是一个方法
        """
        self.method = method
        self.status = 200
        self.msg = None
        self.kwargs = kwargs

    def __str__(self):
        return "<Valid: %s>" % self.method

    def __repr__(self):
        return "<Valid: %s>" % self.method

    def __call__(self, *args, **kwargs):
        return getattr(self, self.method)(*args, **kwargs)

    def enum(self, map):
        map = {str(x): str(y) for x, y in map}
        reverseMap = {str(y): x for x, y in map.items()}

        def inner(data):
            return (map.get(data) and data) or reverseMap.get(data)

        return dict(method=inner, description=map)


class MethodProxy(object):
    kwargs = {}

    def __init__(self, valid_class=None):
        self.valid_class = valid_class

    def __call__(self, *args, **kwargs):
        self.kwargs = kwargs
        return self

    def __getattr__(self, key):
        return self.valid_class(key, **self.kwargs)
