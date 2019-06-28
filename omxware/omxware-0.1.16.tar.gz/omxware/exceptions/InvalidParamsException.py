"""
OMXWare InvalidParams Exception
"""
from omxware.exceptions.Error import Error


class InvalidParamsError(Error):

    def __init__(self, message):
        super().__init__(message)
        self._message = message

    def get_message(self):
        """Return the status code"""
        return self._message
