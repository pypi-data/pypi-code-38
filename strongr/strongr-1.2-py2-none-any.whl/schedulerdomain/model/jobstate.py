from enum import Enum

class JobState(Enum):
    FAILED = -10
    ENQUEUED = 10
    ASSIGNED = 20
    RUNNING = 30
    FINISHED = 40
    ON_HOLD = 50
