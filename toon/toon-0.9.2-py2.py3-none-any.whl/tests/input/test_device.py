from pytest import raises
from tests.input.mockdevices import Dummy, DummyList, NoObs
from toon.input.device import Obs


def test_device_single():
    dev = Dummy()
    with dev:
        res = dev.do_read()
    assert(issubclass(type(res[0]), Obs))
    assert(issubclass(type(res.num1.time), float))
    assert(len(res.num1.data) == 5)


def test_device_multi():
    dev = DummyList()
    with dev:
        res = dev.do_read()
    assert(len(res) == 2)


def test_context():
    dev = Dummy()
    with dev:
        res = dev.do_read()
    assert(issubclass(type(res[0]), Obs))
    assert(issubclass(type(res.num1.time), float))
    assert(len(res.num1.data) == 5)


def test_no_obs():
    dev = NoObs()
    with raises(ValueError):
        with dev:
            dev.read()
