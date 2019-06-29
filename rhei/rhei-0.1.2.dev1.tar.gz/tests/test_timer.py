from rhei import Timer, TimerState


def test_basic_timing(time_mock):
    time_mock.return_value = 100
    timer = Timer()
    assert timer.get() == 0.0
    assert timer.state == TimerState.PAUSED
    time_mock.return_value = 110
    timer.start()
    assert timer.state == TimerState.COUNTING

    time_mock.return_value = 120
    assert timer.get() == 10


def test_pausing(time_mock):
    time_mock.return_value = 100
    timer = Timer()
    timer.start()
    assert timer.state == TimerState.COUNTING

    time_mock.return_value = 110
    assert timer.get() == 10

    timer.pause()
    time_mock.return_value = 120
    assert timer.get() == 10
    assert timer.state == TimerState.PAUSED

    timer.start()
    time_mock.return_value = 130
    assert timer.get() == 20
    assert timer.state == TimerState.COUNTING

    timer.pause()
    time_mock.return_value = 140
    assert timer.get() == 20
    assert timer.state == TimerState.PAUSED

    timer.start()
    time_mock.return_value = 150
    assert timer.get() == 30
    assert timer.state == TimerState.COUNTING


def test_pausing_twice(time_mock):
    time_mock.return_value = 0
    timer = Timer()
    timer.start()
    assert timer.state == TimerState.COUNTING

    time_mock.return_value = 10
    assert timer.get() == 10
    assert timer.state == TimerState.COUNTING

    time_mock.return_value = 20
    timer.pause()
    assert timer.state == TimerState.PAUSED

    time_mock.return_value = 30
    timer.pause()
    assert timer.get() == 20
    assert timer.state == TimerState.PAUSED


def test_resetting(time_mock):
    time_mock.return_value = 0
    timer = Timer()
    timer.start()
    assert timer.state == TimerState.COUNTING

    time_mock.return_value = 10
    assert timer.get() == 10
    assert timer.state == TimerState.COUNTING

    time_mock.return_value = 20
    timer.reset()
    assert timer.get() == 0
    assert timer.state == TimerState.COUNTING

    time_mock.return_value = 30
    assert timer.get() == 10
    assert timer.state == TimerState.COUNTING

    time_mock.return_value = 40
    timer.pause()
    assert timer.get() == 20
    assert timer.state == TimerState.PAUSED


def test_pause_and_reset(time_mock):
    time_mock.return_value = 1000
    timer = Timer()
    timer.start()
    assert timer.state == TimerState.COUNTING

    time_mock.return_value = 1010
    assert timer.get() == 10
    assert timer.state == TimerState.COUNTING

    time_mock.return_value = 1020
    timer.pause()
    assert timer.get() == 20
    assert timer.state == TimerState.PAUSED

    time_mock.return_value = 1030
    timer.reset()
    time_mock.return_value = 1040
    assert timer.get() == 0
    assert timer.state == TimerState.PAUSED
