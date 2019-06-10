import pytest
from unittest.mock import Mock, patch, ANY
from time import sleep, monotonic
from piripherals import ClickButton

T = 0.05  # base time unit
D = 3 * T
H = 10 * T
R = 5 * T


@pytest.fixture
def btn():
    # slow things down for testing
    global clicked, held, button
    clicked, held = Mock(), Mock()
    button = ClickButton(click_time=T, double_click_time=D,
                         hold_time=H, hold_repeat=R,
                         when_clicked=clicked, when_held=held)
    yield button
    print(clicked.mock_calls)
    print(held.mock_calls)


def test_debounce(btn):
    "test debouncing, up/down needs stable input, no clicks are fired"
    # debouncing spurious DOWN
    btn.press()
    assert btn.is_down()
    sleep(T / 2)
    btn.release()  # release quickly
    assert btn.is_down()
    sleep(T)
    btn.release()
    assert btn.is_up()
    sleep(T)

    # debouncing spurious UP
    btn.press()
    assert btn.is_down()
    sleep(T / 2)
    btn.release()  # release, but only short ...
    assert btn.is_down()
    sleep(T / 2)
    btn.press()  # down again
    assert btn.is_down()
    sleep(T)
    btn.release()
    assert btn.is_up()

    # quick UPs and DOWNs
    for i in range(10):
        btn(1)
        assert btn.is_up()
        sleep(T / 2)
        btn(0)
        assert btn.is_up()
        sleep(T / 2)

    # no clicks ro hold detected
    clicked.assert_not_called()
    held.assert_not_called()


def test_single_click(btn):
    btn.press()
    assert btn.is_down()
    sleep(T)
    btn.release()
    assert btn.is_up()
    clicked.assert_not_called()  # should be counted but not yet fired
    sleep(T)
    btn.release()
    assert btn.is_up()
    clicked.assert_not_called()  # should be counted but not yet fired
    sleep(T)
    btn.release()
    assert btn.is_up()
    clicked.assert_not_called()  # should be counted but not yet fired
    sleep(T)
    btn.release()
    assert btn.is_up()
    clicked.assert_called_once_with(1)
    held.assert_not_called()


def test_double_click(btn):
    btn.press()
    assert btn.is_down()
    sleep(T)
    btn.release()
    assert btn.is_up()
    clicked.assert_not_called()  # should be counted but not yet fired
    sleep(T)
    btn.press()  # again
    assert btn.is_down()
    clicked.assert_not_called()  # should be counted but not yet fired
    sleep(T)
    btn.release()  # again
    assert btn.is_up()
    clicked.assert_not_called()  # should be counted but not yet fired
    sleep(D)
    btn.release()
    assert btn.is_up()
    clicked.assert_called_once_with(2)
    held.assert_not_called()


def test_hold(btn):
    btn.press()
    assert btn.is_down()
    assert not btn.is_held()
    held.assert_not_called()
    sleep(H)
    btn.press()
    assert btn.is_held()
    assert btn.is_down()
    sleep(T)
    btn.release()
    assert btn.is_up()
    assert not btn.is_held()
    sleep(D)
    btn.release()
    assert btn.is_up()
    held.assert_called_once_with(0)
    clicked.assert_not_called()


def test_hold_repeat(btn):
    btn.press()
    assert btn.is_down()
    assert not btn.is_held()
    held.assert_not_called()
    sleep(H)
    btn.press()
    assert btn.is_down()
    assert btn.is_held()
    held.assert_called_once_with(0)
    sleep(T)
    btn.press()
    assert btn.is_down()
    held.assert_called_with(0)
    sleep(R - T)
    btn.press()
    assert btn.is_down()
    held.assert_called_with(0)
    sleep(R)
    btn.press()
    assert btn.is_down()
    held.assert_called_with(0)
    assert held.call_count == 3
    clicked.assert_not_called()


def test_click_hold(btn):
    btn.press()
    assert btn.is_down()
    held.assert_not_called()
    sleep(T)
    btn.release()
    assert btn.is_up()
    sleep(D)
    btn.press()
    assert btn.is_down()
    sleep(H)
    btn.press()
    assert btn.is_down()
    held.assert_called_once_with(1)
    clicked.assert_not_called()


def do_click(btn, n):
    for i in range(n):
        btn(1)
        sleep(T)
        btn(0)
        sleep(T)
    sleep(D)
    btn(0)


def do_hold(btn, n):
    for i in range(n):
        btn(1)
        sleep(T)
        btn(0)
        sleep(T)
    btn(1)
    sleep(H)
    btn(1)
    btn(0)


def test_clicks_and_holds(btn):
    do_click(btn, 0)
    clicked.assert_not_called()
    do_click(btn, 1)
    clicked.assert_called_once_with(1)
    do_click(btn, 2)
    clicked.assert_called_with(2)
    do_click(btn, 3)
    clicked.assert_called_with(3)

    held.assert_not_called()

    do_hold(btn, 0)
    held.assert_called_once_with(0)
    do_hold(btn, 1)
    held.assert_called_with(1)
    do_hold(btn, 3)
    held.assert_called_with(3)

    assert clicked.call_count == 3


def test_handlers():
    btn = ClickButton(click_time=T, double_click_time=D,
                      hold_time=H, hold_repeat=R)
    click1 = Mock(side_effect=Exception)  # button must be exception resistant
    btn.on_click(1, click1)
    click2 = Mock(side_effect=Exception)
    btn.on_click(2, click2)
    hold0 = Mock(side_effect=Exception)
    btn.on_hold(0, hold0)
    hold1 = Mock(side_effect=Exception)
    btn.on_hold(1, hold1)

    do_click(btn, 1)
    do_click(btn, 4)
    click1.assert_called_once_with()
    click2.assert_not_called()
    hold0.assert_not_called()
    hold1.assert_not_called()

    do_click(btn, 2)
    do_click(btn, 3)
    click1.assert_called_once_with()
    click2.assert_called_once_with()
    hold0.assert_not_called()
    hold1.assert_not_called()

    do_hold(btn, 0)
    do_hold(btn, 2)
    click1.assert_called_once_with()
    click2.assert_called_once_with()
    hold0.assert_called_once_with()
    hold1.assert_not_called()

    do_hold(btn, 1)
    do_hold(btn, 3)
    click1.assert_called_once_with()
    click2.assert_called_once_with()
    hold0.assert_called_once_with()
    hold1.assert_called_once_with()


@patch('piripherals.button.GPIO', create=1)
def test_gpio(GPIO, btn):
    #btn = ClickButton(pin=4, click_time=T, double_click_time=D, hold_time=H, hold_repeat=R)
    btn.bind(4)

    GPIO.setmode.assert_called_with(GPIO.BCM)
    GPIO.setup.assert_called_with(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect.assert_called_with(4, GPIO.FALLING, ANY)
    irq = GPIO.add_event_detect.call_args[0][2]

    def down():
        GPIO.input.return_value = GPIO.LOW
        irq()

    def up(): GPIO.input.return_value = GPIO.HIGH

    TT, DD, HH = 1.2 * T, 1.2 * D, 1.2 * H

    # single click
    down()
    sleep(T / 10)
    up()  # bounce
    sleep(T / 10)
    down()
    sleep(TT)
    clicked.assert_not_called()
    up()
    clicked.assert_not_called()
    sleep(TT)
    clicked.assert_not_called()
    sleep(DD)
    clicked.assert_called_once_with(1)

    # double click
    down()
    sleep(TT)
    up()
    sleep(TT)
    down()
    sleep(TT)
    up()
    sleep(DD)
    clicked.assert_called_with(2)

    # hold
    down()
    held.assert_not_called()
    sleep(HH)
    held.assert_called_once_with(0)
    up()
    sleep(DD)

    # click hold
    down()
    sleep(TT)
    up()
    sleep(TT)
    down()
    sleep(HH)
    held.assert_called_with(1)
    up()
