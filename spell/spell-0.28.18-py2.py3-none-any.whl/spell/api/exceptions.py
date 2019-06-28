import json

from spell.api import models


class ClientException(Exception):
    """Base exception for all errors encountered communicating with Spell.

    Attributes:
        msg (str): detailed message explaining the exception
        response (:py:class:`requests.Response`): the underlying response that generated the exception
        exception (:py:class:`Exception`): the underlying exception if the exception wraps another exception
    """

    def __init__(self, msg=None, response=None, exception=None):
        if msg is None:
            msg = "A client exception occurred.\n"
            url = getattr(response, "url", None)
            status_code = getattr(response, "status_code", None)
            text = getattr(response, "text", None)
            if url:
                msg += "URL: {}\n".format(url)
            if status_code:
                msg += "Response Status Code: {}\n".format(status_code)
            if text:
                msg += "Response: {}\n".format(text)
            msg = msg.rstrip()
        super(ClientException, self).__init__(msg)
        self.message = msg
        self.response = response
        self.exception = exception


class ServerError(ClientException):
    """An exception indicating an error occurred while processing the request on the Spell server."""

    def __init__(self, msg=None, response=None, exception=None):
        if msg is None:
            msg = "A server error occured.\n"
        super(ServerError, self).__init__(msg, response, exception)


class BadRequest(ClientException):
    """An exception indicating an invalid request was made to the Spell server."""

    def __init__(self, msg=None, response=None, exception=None):
        if msg is None:
            msg = "A bad request was made.\n"
        super(BadRequest, self).__init__(msg, response, exception)


class UnauthorizedRequest(ClientException):
    """An exception indicating an unauthorized request was made to the Spell server."""

    def __init__(self, msg=None, response=None, exception=None):
        if msg is None:
            msg = "An unauthorized request was made.\n"
        super(UnauthorizedRequest, self).__init__(msg, response, exception)


class ConflictRequest(ClientException):
    """An exception indicating the requested action is in conflict with an existing Spell resource."""

    def __init__(self, msg=None, response=None, exception=None):
        if msg is None:
            msg = "A conflicting request was made.\n"
        super(ConflictRequest, self).__init__(msg, response, exception)


class JsonDecodeError(ClientException):
    """An exception indicating there was an error decoding the JSON payload from the Spell server."""

    def __init__(self, msg=None, response=None, exception=None):
        if msg is None:
            msg = "A JSON decoding error occured.\n"
        super(JsonDecodeError, self).__init__(msg, response, exception)


class WaitError(ClientException):
    """An exception indicating there was an error waiting for the requested event on the Spell server."""

    def __init__(self, msg=None, response=None, exception=None):
        if msg is None:
            msg = "An error occured waiting for the server.\n"
        super(WaitError, self).__init__(msg, response, exception)


def decode_error(response):
    try:
        return json.loads(response.text, object_hook=models.Error.response_dict_to_object)
    except Exception:
        return None
