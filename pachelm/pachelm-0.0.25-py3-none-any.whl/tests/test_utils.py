import pytest
from pachelm.utils import map_nested_dicts_modify, map_nested_dicts_modify_key, convert

def test_map_nested_dicts_modify():
    obj = { 'a': 1, 'b': 2, 'c': { 'x': 3, 'y': 4 }}
    expected = { 'a': 10, 'b': 20, 'c': { 'x': 30, 'y': 40 }}
    map_nested_dicts_modify(obj, lambda x: x * 10)
    assert obj == expected

def test_map_nested_dicts_modify_key():
    obj = { 'aBout': 1, 'b': 2, 'c': { 'imagePullSecrets': 3, 'y': 4 }}
    expected = { 'a_bout': 1, 'b': 2, 'c': { 'image_pull_secrets': 3, 'y': 4 }}
    ouput = map_nested_dicts_modify_key(obj, convert)
    assert ouput == expected
