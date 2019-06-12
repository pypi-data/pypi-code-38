from enum import IntEnum


class CeleryHookNames(IntEnum):
    before_worker_start = 0
    after_worker_stop = 3
    before_beat_start = 4
    after_beat_start = 7
