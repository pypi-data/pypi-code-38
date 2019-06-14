from urllib.parse import urlsplit

from mohawk import Receiver, Sender
from mohawk.exc import HawkFail


default_content_type = 'text/plain'
default_content = ''


class RequestSigner:
    algorithm = 'sha256'
    header_name = 'X-Signature'
    secret = None
    sender_id = None

    def __init__(self, secret, sender_id):
        self.secret = secret
        self.sender_id = sender_id

    def get_signature_headers(self, url, body, method, content_type):
        sender = Sender(
            {
                'id': self.sender_id,
                'key': self.secret,
                'algorithm': self.algorithm
            },
            get_path(url),
            method,
            content=get_content(body),
            content_type=get_content_type(content_type),
        )

        return {
            self.header_name: sender.request_header
        }


class RequestSignatureChecker:
    header_name = 'HTTP_X_SIGNATURE'
    secret = None
    algorithm = 'sha256'

    def __init__(self, secret):
        self.secret = secret

    def lookup_credentials(self, sender_id):
        return {
            'id': sender_id,
            'key': self.secret,
            'algorithm': self.algorithm
        }

    def test_signature(self, request):
        """
        Thest that the signature header matches the expected value.

        Args
            request (django.http.Request): The request to check the properties.
        Returns:
            bool or Receiver : False if rejected, Receiver instance if accepted

        """

        content_type = get_content_type(request.META.get('CONTENT_TYPE'))
        try:
            return Receiver(
                self.lookup_credentials,
                request.META.get(self.header_name),
                request.get_full_path(),
                request.method,
                content=get_content(request.body),
                content_type=get_content_type(content_type),
            )
        except HawkFail:
            return False


def get_path(url):
    """
    Get the path from a given url, including the querystring.

    Args:
        url (str)
    Returns:
        str

    """

    url = urlsplit(url)
    path = url.path
    if url.query:
        path += "?{}".format(url.query)
    return path


def get_content_type(content_type):
    return default_content_type if content_type is None else content_type


def get_content(content):
    return default_content if content is None else content
