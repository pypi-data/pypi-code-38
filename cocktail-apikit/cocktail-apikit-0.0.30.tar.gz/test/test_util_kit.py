#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Creation: 4/17/19 7:31 PM
@Author: liang
@File: test_util_kit.py
"""
import pytest
import uuid
from bson.binary import Binary, STANDARD
from cocktail_apikit.utils_kit import dict_attr, build_mongodb_uuid, convert_py_uuid_to_mongodb_uuid


@pytest.fixture
def dict_obj():
    return {'type': 'book', 'author': {'name': 'test', 'email': 'test@mail.com', 'meta': {'age': 10}}}


def test_dict_attr(dict_obj):
    assert dict_attr(None) is None
    assert dict_attr('', None) is None
    assert dict_attr(None, None) is None

    assert dict_attr(dict_obj, 'name') is None
    assert dict_attr(dict_obj, 'type') == 'book'
    assert isinstance(dict_attr(dict_obj, 'author'), dict)

    assert dict_attr(dict_obj, 'author.nothing') is None
    assert dict_attr(dict_obj, 'author.name') == 'test'
    assert dict_attr(dict_obj, 'author.email') == 'test@mail.com'

    assert dict_attr(dict_obj, 'author.meta.age') == 10


def test_build_mongodb_uuid_with_none_or_empty_ok():
    """
    If the value is none or empty, then create a mongo standard uuid
    object the a new UUID object
    """
    value = build_mongodb_uuid(None)
    assert value 
    assert isinstance(value, Binary) and value.subtype == STANDARD

    value = build_mongodb_uuid()
    assert value 
    assert isinstance(value, Binary) and value.subtype == STANDARD


def test_build_mongodb_uuid_with_uuid_obj_ok():
    """
    If the value is an uuid instance object, then return the corresponding 
    mongo standard uuid
    """
    value = uuid.uuid4()

    mongo_uuid = build_mongodb_uuid(value)

    assert mongo_uuid
    assert isinstance(mongo_uuid, Binary) and mongo_uuid.subtype == STANDARD


def test_build_mongodb_uuid_with_already_mongo_uuid_ok():
    """
    If the value is already a standard mongo uuid object, will just return it
    instead of raise Exception
    """
    value = build_mongodb_uuid()
    mongo_uuid = build_mongodb_uuid(value)
    assert mongo_uuid
    assert isinstance(mongo_uuid, Binary) and mongo_uuid.subtype == STANDARD


def test_convert_mongodb_uuid_with_invalid_uuid_string_fail():
    value = 'any string value instead of uuid'
    with pytest.raises(ValueError):
        convert_py_uuid_to_mongodb_uuid(value)


def test_convert_mongodb_uuid_with_valid_uuid_string_ok():
    value = uuid.uuid4().hex
    mongo_uuid = convert_py_uuid_to_mongodb_uuid(value)
    assert mongo_uuid
    assert isinstance(mongo_uuid, Binary) and mongo_uuid.subtype == STANDARD


def test_convert_mongodb_uuid_with_uuid_obj_ok():
    value = uuid.uuid4()
    mongo_uuid = convert_py_uuid_to_mongodb_uuid(value)
    assert mongo_uuid
    assert isinstance(mongo_uuid, Binary) and mongo_uuid.subtype == STANDARD
