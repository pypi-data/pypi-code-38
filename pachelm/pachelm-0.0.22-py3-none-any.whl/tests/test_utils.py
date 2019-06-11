import pytest
from pachelm.utils import map_nested_dicts_modify

def test_map_nested_dicts_modify():
    obj = { 'a': 1, 'b': 2, 'c': { 'x': 3, 'y': 4 }}
    expected = { 'a': 10, 'b': 20, 'c': { 'x': 30, 'y': 40 }}
    map_nested_dicts_modify(obj, lambda x: x * 10)
    assert obj == expected
