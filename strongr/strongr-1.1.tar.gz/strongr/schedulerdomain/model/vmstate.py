from enum import Enum

class VmState(Enum):
    FAILURE = -10
    NEW = 10
    PROVISION = 20
    READY = 30
    LOCKED = 40
    MARKED_FOR_DEATH = 50
    DESTROYED = 60
