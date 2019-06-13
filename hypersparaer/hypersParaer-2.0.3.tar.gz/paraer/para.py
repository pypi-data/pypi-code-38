# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import functools
import traceback
import uuid
from django.conf import settings

from django.utils.module_loading import import_string

from .datastrctures import Valid


def _doc_generater(itemset, func):
    """
    itemset
    """
    func_name = func.__name__

    title = (func.__doc__ or "").strip("\n").strip() or func.__name__

    parameters = [_defaulter(x, func_name) for x in itemset]
    swagger = dict(title=title, parameters=parameters)
    return swagger


def para_ok_or_400(itemset):
    """
    验证参数值, 参数不对则返回400, 若参数正确则返回验证后的值, 并且根据itemset中的值，来生成func的__doc__
    name: 需要校验的参数名称
    method: 校验方法, 校验成功时， 则返回校验方法后的校验值
    required: 是否可以为空,  当GET或者POST,或者request参数为 '', None 时，判定为空, 当参数为False, 0判定为非空
    msg: 校验失败返回的错误消息
    replace: 校验正确后返回的值对应的key
    description: 对参数的描述
    in: path, querystring, formData
    type: 参数类型(string, integer, array, object, boolean), 目前根据_get_type_by_name方法来判定
    参考 https://swagger.io/docs/specification/data-models/data-types/
    
    
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(cls, request, *args, **kwargs):
            paramap = dict(kwargs)
            paramap.setdefault(
                "id", kwargs.get("pk", None)
            )  # Serializer fields中生成的为id 这个key， 但是django解析url中为 pk这个pk，为了不在文档中生成id 和pk这两个field， 所以都统一用id这个key， 那么在itemset中也写id这个key
            data = request.GET or request.data
            result = cls.result_class()  # 继承与Result类
            paramap.update({x: y for x, y in data.items()})
            [_check_para(request, result, kwargs, item, paramap) for item in itemset]
            if not result:
                return result()
            return func(cls, request, *args, **kwargs)

        swagger = _doc_generater(itemset, func)
        wrapper.__swagger__ = swagger
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper

    return decorator


def perm_ok_or_403(itemset):
    """验证参数值, 参数不对则返回400, 若参数正确则返回验证后的值"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(cls, request, *args, **kwargs):
            for item in itemset:
                before, method, reason = (
                    item.get("before"),
                    item["method"],
                    item["reason"],
                )
                before and before(request, kwargs)
                try:
                    perm = method(request, kwargs)
                except Exception:
                    perm = None
                    if settings.DEBUG:
                        traceback.print_exc()
                if not perm:
                    return cls.result_class().status(403, reason)()
            return func(cls, request, *args, **kwargs)

        return wrapper

    return decorator


def make_markdown_table(array: list, title=None):
    """把数组转为markdown格式的字符串
    :array: [['title', 'value'], ['asd', '1']]
    """

    if title:
        array.insert(0, title)
    markdown = "\n" + str("| ")

    for e in array[0]:
        to_add = " " + str(e) + str(" |")
        markdown += to_add
    markdown += "\n"

    markdown += "|"
    for i in range(len(array[0])):
        markdown += str("-------------- | ")
    markdown += "\n"

    for entry in array[1:]:
        markdown += str("| ")
        for e in entry:
            to_add = str(e) + str(" | ")
            markdown += to_add
        markdown += "\n"

    return markdown + "\n"


def _parse_description(item: dict):
    description = item.get("description") or item.get("msg") or "description"
    if isinstance(description, dict):
        description = [(key, value) for key, value in description.items()]
    if isinstance(description, list):
        description = make_markdown_table(description, title=["值", "描述"])
    return description


def _get_type_by_name(name):
    if name.endswith("id"):
        return "integer"
    if any(x in name for x in ["date", "start", "end"]):
        return "date"
    return "string"


def _check_para(request, result, kwargs, item, paramap):
    """
    根据参数校验值来更新result类和kwargs参数
    :request: Request
    :result: Result
    :kwargs: dict 视图函数的关键字参数
    :item: dict para_ok_or_400参数中的元素

    """
    name, v, msg = [item[x] for x in ["name", "method", "msg"]]
    value = None  # 与 '' 区别
    para = paramap.get(name)
    if item["required"] and para in (None, ""):  # 如果是post方法并且传参是json的话，para可能为0
        return result.error(name, "required").status(422)
    # GET 方法时不区分 '' 和不传这个参数的情况
    if not (request.method == "GET" and not para):
        try:
            value = v(para)
        except Exception:
            if settings.DEBUG:
                traceback.print_exc()
        msg = v.msg or msg
        if v.status == 403:  # 权限错误时直接返回错误
            return result.status(v.status, msg)
        if value in (None, False):
            return result.error(name, msg).status(422)
        # 优先取item[mehotd]校验方法的返回值作为view的传入参数，如校验返回值为True，则取GET或request.data的值
        if value is True:
            value = para
        kwargs.update({item["replace"] or name: value})  # method 返回了非布尔值则更新kwargs
    return result, kwargs


def _check_para_type(item, value):
    type = item["type"]
    if type == "object":
        return isinstance(value, dict)
    if type == "array":
        return isinstance(value, list)
    if type == "boolean":
        return isinstance(value, bool)
    if type == "integer":
        return str(value).isdigit()
    if type == "string":
        return isinstance(value, str)
    return False


_locationmap = {
    "get": "query",
    "list": "query",
    "retrieve": "query",
    "update": "formData",
    "create": "formData",
    "post": "formData",
}


def _defaulter(item, func_name):
    """设置默认参数"""

    location = _locationmap.get(func_name, "query")
    item.setdefault("in", location)
    required = item["in"] == "path"
    item.setdefault("method", lambda x: x)
    item["name"] == "pk" and item.update(
        name="id", type="integer", required=item.get("required", True)
    )
    item.setdefault("required", required)
    item.setdefault("type", _get_type_by_name(item["name"]))

    item["description"] = _parse_description(item)
    msg = item.get("description") or ""
    item.setdefault("msg", msg)
    item.setdefault("replace", None)
    method = item["method"]
    if not isinstance(method, Valid):  # 把lambda函数替换为Valid对象
        name = uuid.uuid1().hex
        v = Valid(name)
        setattr(v, name, method)
        item["method"] = v
    return item
