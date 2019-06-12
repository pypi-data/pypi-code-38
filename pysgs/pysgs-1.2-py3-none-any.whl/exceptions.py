"""
Set of exceptions to use with pysgs module
"""


class SGSError(Exception):
    """
    General module exception
    """

    def __init__(self, message):
        """
        Initialize general error exception
        """

        Exception.__init__(self, message)
