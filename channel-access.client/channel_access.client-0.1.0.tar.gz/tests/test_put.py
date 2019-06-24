import pytest

import channel_access.common as ca
import channel_access.client as cac
from . import common




@pytest.mark.parametrize("type_", common.INT_TYPES)
def test_put_int(server, client, type_):
    s_pv = server.createPV('CAS:Test', type_)
    c_pv = client.createPV('CAS:Test', monitor=False, initialize=cac.InitData.NONE)
    c_pv.ensure_connected(timeout=0.1)
    c_pv.put(42)
    assert(s_pv.value == 42)
    c_pv.disconnect()

@pytest.mark.parametrize("type_", common.FLOAT_TYPES)
def test_put_float(server, client, type_):
    s_pv = server.createPV('CAS:Test', type_)
    c_pv = client.createPV('CAS:Test', monitor=False, initialize=cac.InitData.NONE)
    c_pv.ensure_connected(timeout=0.1)
    c_pv.put(3.141)
    assert(s_pv.value == pytest.approx(3.141))
    c_pv.disconnect()

def test_put_string(server, client):
    s_pv = server.createPV('CAS:Test', ca.Type.STRING)
    c_pv = client.createPV('CAS:Test', monitor=False, initialize=cac.InitData.NONE)
    c_pv.ensure_connected(timeout=0.1)
    c_pv.put('Hello')
    assert(s_pv.value == 'Hello')
    c_pv.disconnect()

def test_put_enum(server, client):
    s_pv = server.createPV('CAS:Test', ca.Type.ENUM, attributes = {
        'enum_strings': ('a', 'b'),
    })
    c_pv = client.createPV('CAS:Test', monitor=False, initialize=cac.InitData.NONE)
    c_pv.ensure_connected(timeout=0.1)
    c_pv.put(1)
    assert(s_pv.value == 1)
    c_pv.put('a')
    assert(s_pv.value == 0)
    c_pv.disconnect()


@pytest.mark.parametrize("type_", common.INT_TYPES)
def test_put_int_array(server, client, type_):
    test_values = tuple(range(10))
    s_pv = server.createPV('CAS:Test', type_, count=len(test_values), use_numpy=False)
    c_pv = client.createPV('CAS:Test', monitor=False, initialize=cac.InitData.NONE)
    c_pv.ensure_connected(timeout=0.1)
    c_pv.put(test_values)
    assert(s_pv.value == test_values)
    c_pv.disconnect()

@pytest.mark.parametrize("type_", common.FLOAT_TYPES)
def test_put_float_array(server, client, type_):
    test_values = tuple( x * 3.141 for x in range(10) )
    s_pv = server.createPV('CAS:Test', type_, count=len(test_values), use_numpy=False)
    c_pv = client.createPV('CAS:Test', monitor=False, initialize=cac.InitData.NONE)
    c_pv.ensure_connected(timeout=0.1)
    c_pv.put(test_values)
    assert(s_pv.value == pytest.approx(test_values))
    c_pv.disconnect()

def test_put_enum_array(server, client):
    strings = ('a', 'b', 'c', 'd')
    test_values = ( 2, 0, 1, 1, 0, 0, 3, 1, 3, 2 )
    s_pv = server.createPV('CAS:Test', ca.Type.ENUM, count=len(test_values), attributes = {
        'enum_strings': strings
    }, use_numpy=False)
    c_pv = client.createPV('CAS:Test', monitor=False, initialize=cac.InitData.NONE)
    c_pv.ensure_connected(timeout=0.1)
    c_pv.put(test_values)
    assert(s_pv.value == test_values)
    s_pv.value = (0,) * len(test_values)
    c_pv.put(tuple( strings[x] for x in test_values ))
    assert(s_pv.value == test_values)
    c_pv.disconnect()
