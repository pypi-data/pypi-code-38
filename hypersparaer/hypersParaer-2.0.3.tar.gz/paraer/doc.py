# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import re

import rest_framework
from django.db import models
from openapi_codec import encode
from openapi_codec.encode import _get_links
from openapi_codec.encode import generate_swagger_object as _generate_swagger_object
from rest_framework.compat import coreapi
from rest_framework.schemas import AutoSchema as Schema

from .datastrctures import Serializer
from .fields import _get_field_description

RE_PATH = re.compile("\{(\w+)\}")  # extract  /{arg1}/{arg2}  to [arg1, arg2]


class SwaggerSchema(Schema):
    def get_swagger_fields(self, path, method):
        """根据para_ok_or_400中注册的字段生成新的coreapi.Field

        :path: str, 该api的路径
        :method: str, 该api的请求方法
        :returns: (Fields()), 该api的参数列表

        """
        view = getattr(self.view, method.lower(), None)  # APIView
        if not view:
            view = getattr(self.view, self.view.action, None)  # ViewSet
        # para_ok_or_400中生成的__swagger__对象
        swagger = getattr(view, "__swagger__", {})
        path_args = {x for x in RE_PATH.findall(path)}
        parameters = swagger.get("parameters", [])
        fields = tuple(
            coreapi.Field(
                name=x["name"],
                location=(x["name"] in path_args and "path") or x["in"],
                required=x["name"] in path_args or x.get("required", False),
                description=x["description"],
                type=x["type"],
            )
            for x in parameters
        )
        return fields

    def get_link(self, path, method, base_url):
        """
        Return a `coreapi.Link` instance for the given endpoint.
        """
        base_url = None  # 当设置url时，生成的path中应该不带url
        link = super(SwaggerSchema, self).get_link(path, method, base_url)
        swagger_fields = self.get_swagger_fields(path, method)
        nameset = {x.name for x in swagger_fields}
        # 去重， 避免重复生成fields
        fields = (
            tuple(
                (x for x in link.fields if (x.name not in nameset and x.name != "id"))
            )
            + swagger_fields
        )
        link = coreapi.Link(
            url=link.url,
            action=link.action,
            encoding=link.encoding,
            fields=fields,
            description=link.description,
        )
        serializer_class = getattr(
            self.view, "serializer_class", None
        )  # Link是不可变的数据结构。。。所以覆盖带下划线的属性,以绕过这个限制
        if serializer_class:
            link.__serializer__ = Serializer(serializer_class=serializer_class)
        return link


def wrap_generator(func):
    def inner(document):
        swagger = _generate_swagger_object(document)
        links = _get_links(document)
        result = {}
        _links = [link[1] for link in links if hasattr(link[1], "__serializer__")]
        [_get_definitions(link.__serializer__, result) for link in _links]
        swagger["definitions"] = result
        return swagger

    return inner


def _get_definitions(serializer, result):
    obj_name = serializer.name
    if obj_name in result:
        return result
    fields = [x for x in serializer.fields if "ManyToOneRel" not in str(x)]
    fields = [x for x in fields if not getattr(x, "remote_field", None)]
    names = (x.name for x in fields)
    properties = {x: _get_field_description(y) for x, y in zip(names, fields)}
    obj = dict(properties=properties, type="object")
    result[obj_name] = obj
    for x in fields:  # 如果有外键关联，则获取外键关系
        if getattr(x, "remote_field", ""):
            new_serializer = Serializer(model=x.related_model)
            result = _get_definitions(new_serializer, result)
    return result


def _get200Response(link):
    """获取当http response code为200时的返回模板

    :link: Link对象
    :returns: {'$ref': '', 'schema': ''}

    """
    serializer = getattr(link, "__serializer__", None)
    tpl = dict(description="Success")
    if not serializer:
        return tpl
    obj_name = serializer.name
    ref = {"$ref": "#/definitions/{}".format(obj_name)}
    if link.action == "get" and "{" not in link.url:
        # 如果是listview， 则返回array对象
        tpl["schema"] = dict(items=ref, type="array")
    else:
        tpl["schema"] = ref
    return tpl


def _get400(link):
    tpl = dict(description="Bad Request")
    return tpl


def _get403(link):
    tpl = dict(description="Forbidden")
    return tpl


def _get_responses(link):
    """
    Returns minimally acceptable responses object based
    on action / method type.
    """
    response_template = {
        "200": _get200Response(link),
        "400": _get400(link),
        "403": _get403(link),
    }
    if link.action.lower() == "delete":
        response_template.pop("200")
        response_template.update({"204": {"description": "Success"}})

    return response_template


def patch_all():

    rest_framework.schemas.AutoSchema = SwaggerSchema
    encode._get_responses = _get_responses
    encode.generate_swagger_object = wrap_generator(_generate_swagger_object)
