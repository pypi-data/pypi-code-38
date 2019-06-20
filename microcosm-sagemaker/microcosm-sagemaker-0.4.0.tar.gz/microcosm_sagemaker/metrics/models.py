"""
SageMaker metrics by CloudWatch.

"""
from enum import Enum, unique


@unique
class MetricMode(Enum):
    TRAINING = "Training"
    DEVELOP = "Develop"


@unique
class MetricUnit(Enum):
    """
    Inexhaustive list of common CloudWatch metric units

    """
    PERCENT = "Percent"
    COUNT = "Count"
    NONE = "None"


class Metric:
    """
    Record of a metric value at one point in time.

    """
    def __init__(self, name, value, unit=MetricUnit.NONE):
        self.name = name
        self.value = value
        self.unit = unit

        if not isinstance(unit, MetricUnit):
            raise ValueError("Metric needs to be of a supported enum")
