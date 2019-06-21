import pytest

import channel_access.common as ca
import channel_access.server as cas
from . import common




@pytest.mark.parametrize("type_", common.INT_TYPES)
def test_put_int(server, type_):
    pv = server.createPV('CAS:Test', type_)
    common.caput('CAS:Test', 42)
    assert(pv.value == 42)

@pytest.mark.parametrize("type_", common.FLOAT_TYPES)
def test_put_float(server, type_):
    pv = server.createPV('CAS:Test', type_)
    common.caput('CAS:Test', 3.141)
    assert(pv.value == pytest.approx(3.141))

def test_put_string(server):
    pv = server.createPV('CAS:Test', ca.Type.STRING)
    common.caput('CAS:Test', 'Hello')
    assert(pv.value == 'Hello')

def test_put_enum(server):
    pv = server.createPV('CAS:Test', ca.Type.ENUM, attributes = {
        'enum_strings': ('a', 'b'),
    })
    common.caput('CAS:Test', 1)
    assert(pv.value == 1)
    common.caput('CAS:Test', 'a')
    assert(pv.value == 0)


@pytest.mark.parametrize("type_", common.INT_TYPES)
def test_put_int_array(server, type_):
    test_values = tuple(range(10))
    pv = server.createPV('CAS:Test', type_, count=len(test_values), use_numpy=False)
    common.caput('CAS:Test', test_values)
    assert(pv.value == test_values)

@pytest.mark.parametrize("type_", common.FLOAT_TYPES)
def test_put_float_array(server, type_):
    test_values = tuple( x * 3.141 for x in range(10) )
    pv = server.createPV('CAS:Test', type_, count=len(test_values), use_numpy=False)
    common.caput('CAS:Test', test_values)
    assert(pv.value == pytest.approx(test_values))

def test_put_enum_array(server):
    strings = ('a', 'b', 'c', 'd')
    test_values = ( 2, 0, 1, 1, 0, 0, 3, 1, 3, 2 )
    pv = server.createPV('CAS:Test', ca.Type.ENUM, count=len(test_values), attributes = {
        'enum_strings': strings
    }, use_numpy=False)
    common.caput('CAS:Test', test_values)
    assert(pv.value == test_values)
    pv.value = (0,) * len(test_values)
    common.caput('CAS:Test', tuple( strings[x] for x in test_values ))
    assert(pv.value == test_values)


@pytest.mark.skipif(not cas.numpy, reason="No numpy support")
@pytest.mark.parametrize("type_", common.INT_TYPES)
def test_put_int_array_numpy(server, type_):
    import numpy

    test_values = numpy.arange(10)
    pv = server.createPV('CAS:Test', type_, count=len(test_values), use_numpy=True)
    common.caput('CAS:Test', test_values)
    assert(isinstance(pv.value, numpy.ndarray))
    assert(numpy.all(numpy.equal(pv.value, test_values)))

@pytest.mark.skipif(not cas.numpy, reason="No numpy support")
@pytest.mark.parametrize("type_", common.FLOAT_TYPES)
def test_put_float_array_numpy(server, type_):
    import numpy

    test_values = 3.141 * numpy.arange(10)
    pv = server.createPV('CAS:Test', type_, count=len(test_values), use_numpy=True)
    common.caput('CAS:Test', test_values)
    assert(isinstance(pv.value, numpy.ndarray))
    assert(numpy.allclose(pv.value, test_values))

@pytest.mark.skipif(not cas.numpy, reason="No numpy support")
def test_put_enum_array_numpy(server):
    import numpy

    strings = ('a', 'b', 'c', 'd')
    test_values = numpy.array([ 2, 0, 1, 1, 0, 0, 3, 1, 3, 2 ])
    pv = server.createPV('CAS:Test', ca.Type.ENUM, count=len(test_values), attributes = {
        'enum_strings': strings
    }, use_numpy=True)
    common.caput('CAS:Test', test_values)
    assert(isinstance(pv.value, numpy.ndarray))
    assert(numpy.all(numpy.equal(pv.value, test_values)))
    pv.value = numpy.zeros(len(test_values))
    common.caput('CAS:Test', tuple( strings[x] for x in test_values ))
    assert(numpy.all(numpy.equal(pv.value, test_values)))
