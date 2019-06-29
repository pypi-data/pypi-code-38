"""learned form MLflow"""


class Performance:
    """
    Metric object.
    """

    def __init__(self, key, value):
        self._key = key
        self._value = value

    @property
    def key(self):
        """String key corresponding to the metric name."""
        return self._key

    @property
    def value(self):
        """Float value of the metric."""
        return self._value
