import pytest

import channel_access.common as ca
import channel_access.client as cac
from . import common




@pytest.mark.parametrize("type_", common.INT_TYPES)
def test_get_int(server, client, type_):
    s_pv = server.createPV('CAS:Test', type_, attributes = {
        'value': 42
    })
    c_pv = client.createPV('CAS:Test', monitor=False, initialize=cac.InitData.NONE)
    c_pv.ensure_connected(timeout=0.1)
    assert(c_pv.get(block=0.1) == s_pv.value)
    c_pv.disconnect()

@pytest.mark.parametrize("type_", common.FLOAT_TYPES)
def test_get_float(server, client, type_):
    s_pv = server.createPV('CAS:Test', type_, attributes = {
        'value': 3.141
    })
    c_pv = client.createPV('CAS:Test', monitor=False, initialize=cac.InitData.NONE)
    c_pv.ensure_connected(timeout=0.1)
    assert(c_pv.get(block=0.1) == pytest.approx(s_pv.value))
    c_pv.disconnect()

def test_get_string(server, client):
    s_pv = server.createPV('CAS:Test', ca.Type.STRING, attributes = {
        'value': 'Hello'
    })
    c_pv = client.createPV('CAS:Test', monitor=False, initialize=cac.InitData.NONE)
    c_pv.ensure_connected(timeout=0.1)
    assert(c_pv.get(block=0.1) == s_pv.value)
    c_pv.disconnect()

def test_get_enum(server, client):
    s_pv = server.createPV('CAS:Test', ca.Type.ENUM, attributes = {
        'enum_strings': ('a', 'b'),
        'value': 1
    })
    c_pv = client.createPV('CAS:Test', monitor=False, initialize=cac.InitData.NONE)
    c_pv.ensure_connected(timeout=0.1)
    assert(c_pv.get(block=0.1) == s_pv.value)
    assert(c_pv.get(block=0.1, as_string=True) == 'b')
    c_pv.disconnect()


@pytest.mark.parametrize("type_", common.INT_TYPES)
def test_get_int_array(server, client, type_):
    s_pv = server.createPV('CAS:Test', type_, count=10, attributes = {
        'value': tuple(range(10))
    }, use_numpy=False)
    c_pv = client.createPV('CAS:Test', monitor=False, initialize=cac.InitData.NONE)
    c_pv.ensure_connected(timeout=0.1)
    assert(c_pv.get(block=0.1) == s_pv.value)
    c_pv.disconnect()

@pytest.mark.parametrize("type_", common.FLOAT_TYPES)
def test_get_float_array(server, client, type_):
    s_pv = server.createPV('CAS:Test', type_, count=10, attributes = {
        'value': tuple( x * 3.141 for x in range(10) )
    }, use_numpy=False)
    c_pv = client.createPV('CAS:Test', monitor=False, initialize=cac.InitData.NONE)
    c_pv.ensure_connected(timeout=0.1)
    assert(c_pv.get(block=0.1) == pytest.approx(s_pv.value))
    c_pv.disconnect()

def test_get_enum_array(server, client):
    strings = ('a', 'b', 'c', 'd')
    s_pv = server.createPV('CAS:Test', ca.Type.ENUM, count=10, attributes = {
        'enum_strings': strings,
        'value': ( 2, 0, 1, 1, 0, 0, 3, 1, 3, 2 )
    }, use_numpy=False)
    c_pv = client.createPV('CAS:Test', monitor=False, initialize=cac.InitData.NONE)
    c_pv.ensure_connected(timeout=0.1)
    assert(c_pv.get(block=0.1) == pytest.approx(s_pv.value))
    assert(c_pv.get(block=0.1, as_string=True) == tuple( strings[x] for x in s_pv.value ))
    c_pv.disconnect()
