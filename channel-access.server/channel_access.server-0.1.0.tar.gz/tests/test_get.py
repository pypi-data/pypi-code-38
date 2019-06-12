import pytest

import channel_access.common as ca
import channel_access.server as cas
from . import common




@pytest.mark.parametrize("type_", common.INT_TYPES)
def test_get_int(server, type_):
    pv = server.createPV('CAS:Test', type_, attributes = {
        'value': 42
    })
    value = int(common.caget('CAS:Test'))
    assert(value == 42)

@pytest.mark.parametrize("type_", common.FLOAT_TYPES)
def test_get_float(server, type_):
    pv = server.createPV('CAS:Test', type_, attributes = {
        'value': 3.141
    })
    value = float(common.caget('CAS:Test'))
    assert(value == pytest.approx(3.141))

def test_get_string(server):
    pv = server.createPV('CAS:Test', ca.Type.STRING, attributes = {
        'value': 'Hello'
    })
    value = common.caget('CAS:Test')
    assert(value == 'Hello')

def test_get_enum(server):
    pv = server.createPV('CAS:Test', ca.Type.ENUM, attributes = {
        'enum_strings': ('a', 'b'),
        'value': 1
    })
    value = int(common.caget('CAS:Test', as_string=False))
    assert(value == 1)
    value = common.caget('CAS:Test', as_string=True)
    assert(value == 'b')


@pytest.mark.parametrize("type_", common.INT_TYPES)
def test_get_int_array(server, type_):
    test_values = tuple(range(10))
    pv = server.createPV('CAS:Test', type_, count=len(test_values), attributes = {
        'value': test_values
    })
    values = tuple(map(int, common.caget('CAS:Test', array=True)))
    assert(values == test_values)

@pytest.mark.parametrize("type_", common.FLOAT_TYPES)
def test_get_float_array(server, type_):
    test_values = tuple( x * 3.141 for x in list(range(10)) )
    pv = server.createPV('CAS:Test', type_, count=len(test_values), attributes = {
        'value': test_values
    })
    values = tuple(map(float, common.caget('CAS:Test', array=True)))
    assert(values == pytest.approx(test_values))

def test_get_enum_array(server):
    strings = ('a', 'b', 'c', 'd')
    test_values = ( 2, 0, 1, 1, 0, 0, 3, 1, 3, 2 )
    pv = server.createPV('CAS:Test', ca.Type.ENUM, count=len(test_values), attributes = {
        'enum_strings': strings,
        'value': test_values
    })
    values = tuple(map(int, common.caget('CAS:Test', as_string=False, array=True)))
    assert(values == test_values)
    values = tuple(common.caget('CAS:Test', as_string=True, array=True))
    assert(values == tuple( strings[x] for x in test_values ))
