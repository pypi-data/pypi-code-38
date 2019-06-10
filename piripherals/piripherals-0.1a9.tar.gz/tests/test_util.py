import pytest
from unittest.mock import Mock, patch
from piripherals.util import *
from time import sleep


def test_fork():
    func = Mock()
    fork(func)
    sleep(0.3)
    func.assert_called_once_with()


def test_not_raising(capsys):
    func = Mock()
    func.side_effect = Exception('Boom!')
    func2 = not_raising(func)
    func2()
    assert func.called
    out, err = capsys.readouterr()
    assert 'Boom!' in err


def test_on_change(tmpdir):
    foo = tmpdir.join('foo')
    print(foo)
    with foo.open('w') as f:
        f.write('foo')
    callback = Mock()
    on_change(str(foo), callback, delay=0.1)
    sleep(0.3)
    assert not callback.called
    with foo.open('w') as f:
        f.write('bar')
    sleep(0.3)
    assert callback.called


@patch('piripherals.util.GPIO', create=True)
def test_irq_handler(gpio, capsys):
    gpio.input.return_value = gpio.HIGH
    callback = Mock()
    # must continue to work, even when exception was raised in callback
    callback.side_effect = Exception('oops')
    h = IRQHandler(4, callback)
    assert len(callback.mock_calls) == 0
    trigger = gpio.add_event_detect.call_args[0][2]
    trigger()
    sleep(0.3)
    assert len(callback.mock_calls) == 1
    trigger()
    sleep(0.3)
    assert len(callback.mock_calls) == 2
    out, err = capsys.readouterr()
    assert 'oops' in err


def test_poller(capsys):
    callback = Mock()
    # must continue to work, even when exception was raised in callback
    callback.side_effect = Exception('oops')
    Poller(callback, delay=0.2)
    sleep(0.3)
    assert len(callback.mock_calls) == 2
    out, err = capsys.readouterr()
    assert 'oops' in err
