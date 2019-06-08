class MisconfiguredException(Exception):

    """
    Exception raised when an error occurs due to misconfiguration
    of the connection exceptions.
    e.g. missing required keys in a dictionary.
    """

    pass


class AuthFailure(Exception):

    """Exception raised when authentication fails.

    Attributes:
        status_code (int): status code of the failed request
        response (str): response body of the failed request

    Parameters:
        message (str): exception message
        errors (dict): dict with that fills out the attributes
            For example::

                {
                    'status_code': 500,
                    'response': 'Server failed'
                }
    """

    def __init__(self, message, errors):
        """Initialize the exception with a message and a set of values."""
        try:
            super(AuthFailure, self).__init__(message)
            self.status_code = errors['status_code']
            self.response = errors['response']
        except KeyError as ke:
            msg = "Error field {} was not provided"
            msg = msg.format(ke.args[0])
            raise MisconfiguredException(msg)


class RequestFailure(Exception):

    """Exception raised when an api requests fails.

    Attributes:
        status_code (int): status code of the failed request
        response (str): response body of the failed request
        method (str): HTTP method of the failed request
        url (str): URL of the failed request
        payload (str): JSON string of the payload being sent with the
            request. If there was no payload this will be None.

    Parameters:
        message (str): exception message
        errors (dict): dict with that fills out the attributes
            For example::

                {
                    'status_code': 500,
                    'response': 'Server failed',
                    'method': 'GET',
                    'url': 'http://url/path/to/api',
                    'payload': '{ "field": "value" }'
                }
    """

    def __init__(self, message, errors):
        """Initialize the exception with a message and a set of values."""
        try:
            super(RequestFailure, self).__init__(message)
            self.method = errors['method']
            self.url = errors['url']
            self.status_code = errors['status_code']
            self.response = errors['response']
            self.payload = errors['payload']
            self.request = errors['request']
        except KeyError as ke:
            msg = "Error field {} was not provided"
            msg = msg.format(ke.args[0])
            raise MisconfiguredException(msg)
