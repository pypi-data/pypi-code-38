from enum import Enum


class Goal(Enum):
    """Specifies whether OPTaaS will aim for the lowest (min) or highest (max) score"""
    min = 0
    max = 1
