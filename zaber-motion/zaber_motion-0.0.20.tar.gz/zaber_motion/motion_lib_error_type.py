from enum import Enum


class MotionLibErrorType(Enum):
    """
    Enumeration of various errors that may occur during usage of the library.
    """

    REQUEST_TIMEOUT = 0
    CONNECTION_CLOSED = 1
    INVALID_ARGUMENT = 2
    OUT_OF_REQUEST_IDS = 3
    INVALID_PACKET = 4
    CONNECTION_FAILED = 5
    UNKNOWN_REQUEST = 6
    COMMAND_FAILED = 7
    DEVICE_DB_FAILED = 8
    INVALID_DATA = 9
    DEVICE_NOT_IDENTIFIED = 10
    CONVERSION_FAILED = 11
    DEVICE_NUMBER_CONFLICT = 12
    NO_DEVICE_FOUND = 13
    MOVEMENT_INTERRUPTED = 14
    MOVEMENT_FAILED = 15
    IO_ERROR = 16
    INVALID_RESPONSE = 17
    NOT_SUPPORTED = 18
    DEVICE_FAILED = 19
    OS_ERROR = 20
