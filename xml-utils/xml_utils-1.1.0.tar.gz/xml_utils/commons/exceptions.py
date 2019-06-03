""" Xml Utils Exceptions
"""


class XMLError(Exception):
    """ Exception raised by XML validation
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class HTMLError(Exception):
    """ Exception raised by HTML parsing
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)
