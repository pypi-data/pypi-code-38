# encoding: utf-8
from __future__ import print_function, unicode_literals

from .para import make_markdown_table


class MethodProxy(object):
    def auto(self, field):
        return dict(format="int64", type="integer")

    def integer(self, field):
        return dict(format="int64", type="integer")

    def smallinteger(self, field):
        return dict(format="int64", type="integer")

    def boolean(self, field):
        return dict(type="string")

    def decimal(self, field):
        return dict(format="int64", type="float")

    def char(self, field):
        return dict(type="string")

    string = char

    def url(self, field):
        return dict(type="string")

    def text(self, field):
        return dict(type="string")

    def file(self, field):
        return dict(type="file")

    def datetime(self, field):
        return dict(format="date-time", type="string")

    date = datetime

    def choice(self, field):
        enum = field.choice_strings_to_values.keys()
        return dict(type="string", enum=enum)

    def nestedserializer(self, field):
        return dict(type="object", description="point to self")

    def email(self, field):
        return dict(type="string", format="email")

    def primarykeyrelated(self, field):
        return {"$ref": "#/definitions/{}".format(key)}

    serializer = primarykeyrelated

    def onetoone(self, field):
        return {
            "$ref": "#/definitions/{}".format(
                field.related_model._meta.object_name.lower()
            )
        }

    def manytomanyrel(self, field):
        return {
            "$ref": "#/definitions/{}".format(
                field.related_model._meta.object_name.lower()
            )
        }

    manytomany = onetoonerel = manytoonerel = foreignkey = onetoone

    def image(self, field):
        return dict(type="file")

    def serializermethod(self, field):
        return dict(type="string")


proxy = MethodProxy()


def _get_field_name(field):
    """根据field获取field的名称

    :field: Field
    :returns: str

    """
    field = field.__class__.__name__.lower().split("field")[0]
    if field.endswith("serializer"):
        return "serializer"
    return field


def _get_description(field):
    description = getattr(field, "verbose_name", None)
    if description is None:
        description = field.remote_field.verbose_name
    return str(description)


def _get_field_description(field):
    """获取field的swagger描述

    :field: Field对象
    :returns: {"description": "描述", "enum": "枚举值"}

    """
    if field:
        name = _get_field_name(field)
    if name == "onetoonerel":
        field = field.remote_field
    data = getattr(proxy, name, proxy.text)(field)
    if name == "manytomanyrel":
        field = field.remote_field
    data["description"] = _get_description(field)
    if hasattr(field, "choices") and field.choices:
        data["description"] = make_markdown_table(choices, (data["description"], "值"))
        data["enum"] = [x[0] for x in field.choices]
    return data
