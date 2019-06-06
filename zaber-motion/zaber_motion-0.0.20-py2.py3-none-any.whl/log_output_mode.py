from enum import Enum


class LogOutputMode(Enum):
    """
    Mode of logging output of the library.
    """

    OFF = 0
    STDOUT = 1
    STDERR = 2
    FILE = 3
