"""
Tests of the openapi schema in kleinish
"""
from collections import OrderedDict
from inspect import cleandoc

import yaml

from crosscap import openapi


def test_orderedDict():
    """
    Do I keep the order of dicts?
    """
    dct = OrderedDict()
    dct['a'] = 1
    dct['z'] = 2
    dct['b'] = 3
    dct['y'] = 4
    dct['c'] = 5
    dct['x'] = 6
    assert yaml.dump(dct, default_flow_style=False) == cleandoc('''
        a: 1
        z: 2
        b: 3
        y: 4
        c: 5
        x: 6
        ''') + '\n'


def test_helperMediaTypes():
    """
    Do I produce a Responses object with the right data?
    """
    h1 = openapi.textHTML()
    assert isinstance(h1, openapi.OpenAPIResponses)
    assert yaml.load(yaml.dump(h1)) == {
        'default': {'content': {'text/html': {}}}
    }
    h2 = openapi.textHTML({'a': 1})
    assert yaml.load(yaml.dump(h2)) == {
        'default': {'content': {'text/html': {'a': 1}}}
    }
    j1 = openapi.applicationJSON()
    assert isinstance(j1, openapi.OpenAPIResponses)
    assert yaml.load(yaml.dump(j1)) == {
        'default': {'content': {'application/json': {}}}
    }
    j2 = openapi.applicationJSON({'a': 1})
    assert yaml.load(yaml.dump(j2)) == {
        'default': {'content': {'application/json': {'a': 1}}}
    }
