# coding:utf-8

from bson.objectid import ObjectId


def bson_id(src_id=None):
    """
    默认生成ObjectID对象类型的ID
    :param src_id: 任意字符串、数字或者空
    :return: 字符串或者数字
    """
    if src_id is None:
        return ObjectId()

    if isinstance(src_id, str):
        src_id = src_id.lower()
        if ObjectId.is_valid(src_id):
            return ObjectId(src_id)
        elif len(src_id) == 0:
            return ObjectId()

    return src_id


def json_id(src_id=None):
    """
    默认生成ObjectID规范且转为字符串的ID
    :param src_id: 任意字符串、数字或者空
    :return: 字符串或者数字
    """
    if src_id is None:
        return ObjectId().__str__()

    if isinstance(src_id, ObjectId):
        return src_id.__str__()

    if isinstance(src_id, str):
        if len(src_id) == 0:
            return ObjectId().__str__()
        src_id = src_id.lower()

    return src_id


def bson2json(bson_dic):
    for k, v in bson_dic.items():
        if isinstance(v, ObjectId):
            bson_dic[k] = json_id(v)
    return bson_dic


def json2bson(json_dic):
    for k, v in json_dic.items():
        if ObjectId.is_valid(v):
            json_dic[k] = bson_id(v)
    return json_dic
