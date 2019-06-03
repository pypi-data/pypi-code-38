""" Parser Exceptions
"""


class ParserError(Exception):
    """
        Exception raised by the parser
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class RendererError(Exception):
    """
        Exception raised by the renderer
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)