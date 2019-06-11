# -*- coding: utf-8 -*-

"""Various constants
"""

from enum import Enum, auto


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


class OutputFmt(AutoName):
    """List of output formats supported
    """
    json = auto()
    pandas = auto()


class TopicName(AutoName):
    """List of API topics supported
    """
    flow = auto()
    balance = auto()
    frequency = auto()
