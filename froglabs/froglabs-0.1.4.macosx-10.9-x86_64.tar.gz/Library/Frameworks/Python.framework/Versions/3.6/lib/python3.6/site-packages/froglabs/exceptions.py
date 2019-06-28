"""Exceptions."""


__copyright__ = 'Copyright 2019 Froglabs, Inc.'


class Error(Exception):
    """Base Froglabs client exception."""


class HttpError(Error):
    """Base HTTP error."""

    def __init__(self, response):
        content = response.json()
        self.status_code = response.status_code
        self.error_message = content
        super(HttpError, self).__init__(str(self))

    def __str__(self):
        return ('HTTP %s returned with message, %r' %
                (self.status_code, self.error_message))
