"""
Exceptions and helper methods.
"""


class InvalidConfigException(Exception):
    """
    Raised when we fail to load a configuration file.
    """
    def __init__(self, message):
        self.value = message

    def __str__(self):
        return repr(self.value)


def get_or_raise_config_exception(data, key):
    """
    Helper method to raise InvalidConfigException if key not in data.
    :param data: dict: object to get value from
    :param key: str: name of the key we should get a value for
    :return: object: value found in dict
    """
    if not key in data:
        raise InvalidConfigException("Missing {} from config file".format(key))
    return data[key]


class JobStepFailed(Exception):
    """
    Raised when a job step failed
    """
    def __init__(self, message, details):
        self.value = message
        self.details = details

    def __str__(self):
        return repr(self.value)
