import time
from enum import Enum


class TimerState(Enum):
    COUNTING = 1
    PAUSED = 2


class Timer:
    def __init__(self) -> None:
        current_time = float(time.time())
        self._state: TimerState = TimerState.PAUSED
        self._time_coef: float = current_time
        self._pause_time_start: float = current_time

    @property
    def state(self) -> TimerState:
        return self._state

    def start(self) -> None:
        if self._state == TimerState.PAUSED:
            self._time_coef += float(time.time()) - self._pause_time_start

        self._state = TimerState.COUNTING
        self._pause_time_start = 0.0

    def pause(self) -> None:
        if self._state == TimerState.PAUSED:
            return

        self._state = TimerState.PAUSED
        self._pause_time_start = float(time.time())

    def reset(self) -> None:
        current_time = float(time.time())
        self._time_coef: float = current_time
        self._pause_time_start: float = current_time

    def get(self) -> float:
        if self._state == TimerState.PAUSED:
            return -self._time_coef + self._pause_time_start
        else:
            return float(time.time()) - self._time_coef
