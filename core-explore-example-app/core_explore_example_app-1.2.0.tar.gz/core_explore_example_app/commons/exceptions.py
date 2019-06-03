""" Core Explore Example exceptions
"""


class MongoQueryException(Exception):
    """
        Exception raised by mongo query builder
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)
