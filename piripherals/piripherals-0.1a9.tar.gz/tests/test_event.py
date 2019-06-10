import pytest
from unittest.mock import Mock
from time import sleep
from piripherals.event import EventLoop
from piripherals import Event


def test_loop():
    loop = EventLoop()
    func = Mock()
    func.side_effect = lambda: func.inloop(loop.in_loop())
    loop << func
    sleep(0.1)  # delay for loop thread to run
    func.assert_called_once_with()
    func.inloop.assert_called_once_with(True)

    # and again with Exception
    func.side_effect = Exception
    loop << func << func
    sleep(0.1)
    assert func.call_count == 3


def test_event():
    h1, h2 = Mock(), Mock(side_effect=Exception)
    event = Event()
    event >> h1 >> h2
    event.fire('foo')
    h1.assert_called_once_with('foo')
    h2.assert_called_once_with('foo')

    h3 = Mock()
    h3.side_effect = lambda *x: h3.inloop(Event.loop.in_loop())
    event >> h3
    event.fire('bar')
    h1.assert_called_with('bar')
    h2.assert_called_with('bar')
    h3.assert_called_with('bar')
    h3.inloop.assert_called_once_with(False)

    event.remove(h2)
    event.queue('lorem', 'ipsum')
    sleep(0.1)
    h1.assert_called_with('lorem', 'ipsum')
    assert h2.call_count == 2
    h3.assert_called_with('lorem', 'ipsum')
    h3.inloop.assert_called_with(True)


def test_event_partial():
    handler = Mock()
    event = Event() >> handler
    partial_event = event.partial('foo', x=5)
    partial_event.fire('bar')
    handler.assert_called_once_with('foo', 'bar', x=5)


def test_event_conditional():
    handler = Mock()
    condition = Mock(return_value=False)
    event = Event() >> handler
    conditional_event = event & condition
    conditional_event.fire(42)
    handler.assert_not_called()

    condition.return_value = True
    conditional_event.fire(42)
    handler.assert_called_once_with(42)


def test_event_join():
    h1, h2 = Mock(), Mock()
    e1, e2 = Event() >> h1, Event() >> h2
    combined_event = e1 + e2
    assert combined_event is not e1
    assert combined_event is not e2

    e1.fire()
    assert h1.call_count == 1
    assert h2.call_count == 0

    e2.fire()
    assert h1.call_count == 1
    assert h2.call_count == 1

    combined_event.fire()
    assert h1.call_count == 2
    assert h2.call_count == 2


def test_event_join_with_func():
    h1, h2 = Mock(), Mock()
    e1 = Event() >> h1
    combined_event = e1 + h2
    assert combined_event is not e1

    e1.fire()
    assert h1.call_count == 1
    assert h2.call_count == 0

    combined_event.fire()
    assert h1.call_count == 2
    assert h2.call_count == 1


def test_event_as_handler():
    h1, h2 = Mock(), Mock()
    e1, e2 = Event() >> h1, Event() >> h2
    combined_event = e1 >> e2
    assert combined_event is e1
    assert combined_event is not e2

    e1.fire()
    assert h1.call_count == 1
    assert h2.call_count == 1

    e2.fire()
    assert h1.call_count == 1
    assert h2.call_count == 2

    combined_event.fire()
    assert h1.call_count == 2
    assert h2.call_count == 3
