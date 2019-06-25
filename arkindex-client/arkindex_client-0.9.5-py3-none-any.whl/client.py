"""
Arkindex API Client
"""
import os
import apistar
import logging
import yaml
from arkindex.auth import TokenSessionAuthentication
from arkindex.pagination import ResponsePaginator
from arkindex.encoders import XMLEncoder
from io import FileIO
from time import sleep
from urllib.parse import urlsplit, urlunsplit

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

logger = logging.getLogger(__name__)


def options_from_env():
    """
    Get API client keyword arguments from environment variables.
    """
    options = {}
    if 'ARKINDEX_API_TOKEN' in os.environ:
        options['token'] = os.environ.get('ARKINDEX_API_TOKEN')

    if 'ARKINDEX_API_INTERNAL_URL' in os.environ:
        options['base_url'] = os.environ.get('ARKINDEX_API_INTERNAL_URL')
    elif 'ARKINDEX_API_URL' in os.environ:
        options['base_url'] = os.environ.get('ARKINDEX_API_URL')

    return options


class ArkindexClient(apistar.Client):
    """
    An Arkindex API client.
    """

    def __init__(self, token=None, base_url=None, sleep=0, **kwargs):
        r"""
        :param token: An API token to use. If omitted, access is restricted to public endpoints.
        :type token: str or None
        :param base_url: A custom base URL for the client. If omitted, defaults to the Arkindex main server.
        :type base_url: str or None
        :param float sleep: Number of seconds to wait before sending each API request,
           as a simple means of throttling.
        :param \**kwargs: Keyword arguments to send to ``apistar.Client``.
        """
        with open(os.path.join(BASE_DIR, 'schema.yml')) as f:
            schema = yaml.safe_load(f.read())

        super().__init__(schema, **kwargs)
        # Remove domains from each endpoint; allows APIStar to properly handle our base URL
        for link_info in self.document.walk_links():
            original_url = urlsplit(link_info.link.url)
            # Removes the scheme and netloc
            new_url = ('', '', *original_url[2:])
            link_info.link.url = urlunsplit(new_url)

        self.configure(token=token, base_url=base_url, sleep=sleep)

    def __repr__(self):
        return '<{} on {}>'.format(self.__class__.__name__, self.document.url)

    def configure(self, token=None, base_url=None, sleep=None):
        """
        Reconfigure the API client.

        :param token: An API token to use. If omitted, access is restricted to public endpoints.
        :type token: str or None
        :param base_url: A custom base URL for the client. If omitted, defaults to the Arkindex main server.
        :type base_url: str or None
        :param float sleep: Number of seconds to wait before sending each API request,
           as a simple means of throttling.
        """
        self.transport.session.auth = TokenSessionAuthentication(token)

        if not sleep or not isinstance(sleep, float) or sleep < 0:
            self.sleep_duration = 0
        self.sleep_duration = sleep

        if base_url:
            self.document.url = base_url

        # Add the Referer header to allow Django CSRF to function
        self.transport.headers.setdefault('Referer', self.document.url)

        # Add the XML encoder
        if not any(isinstance(e, XMLEncoder) for e in self.transport.encoders):
            self.transport.encoders.append(XMLEncoder())

    def paginate(self, *args, **kwargs):
        """
        Perform a usual request as done by APIStar, but handle paginated endpoints.

        :return: An iterator for a paginated endpoint.
        :rtype: arkindex.pagination.ResponsePaginator
        """
        return ResponsePaginator(self, *args, **kwargs)

    def login(self, email, password):
        """
        Login to Arkindex using an email/password combination.
        This helper method automatically sets the client's authentication settings with the token.
        """
        resp = self.request('Login', body={'email': email, 'password': password})
        if 'auth_token' in resp:
            self.transport.session.auth.token = resp['auth_token']
        return resp

    def request(self, *args, **kwargs):
        """
        Perform an API request.
        :param args: Arguments passed to the APIStar client.
        :param kwargs: Keyword arguments passed to the APIStar client.
        """
        if self.sleep_duration:
            logger.debug('Delaying request by {:f} seconds...'.format(self.sleep_duration))
            sleep(self.sleep_duration)
        return super().request(*args, **kwargs)

    def custom_request(self, operation_id, content=None, encoding='text/plain', **params):
        """
        Helper method to build requests that are not JSON, as APIStar does not
        currently handle anything that is not JSON.

        :param str operation_id: An OpenAPI operation ID.
        :param content: Any kind of content to be send to
           the APIStar transport layer directly.
        :param str encoding: A MIME type to use as the Content-Type for the request.
        :param params: Query parameters for the given operation.
        """
        link = self.lookup_operation(operation_id)
        url = self.get_url(link, params)
        query_params = self.get_query_params(link, params)

        if self.sleep_duration:
            logger.debug('Delaying request by {:f} seconds...'.format(self.sleep_duration))
            sleep(self.sleep_duration)

        return self.transport.send(
            link.method,
            url,
            query_params=query_params,
            content=content,
            encoding=encoding,
        )

    def upload(self, corpus_id, f, mode='rb'):
        """
        Upload a file-like object or a file path to a corpus.
        This helper is required as APIStar does not currently handle
        anything else than JSON as request parameters.

        :param str corpus_id: ID of a writable corpus to upload files to.
        :param f: File-like object, or path to a readable file, to upload.
        :type f: str or file-like object
        :param str mode: When specifying a path, sets the mode to use when
           opening the file.
        :return: The JSON response from the endpoint
        :rtype: dict
        """
        if isinstance(f, str):
            assert os.path.exists(f), 'File {} does not exist'.format(f)
            f = open(f, mode)

        return self.custom_request(
            'UploadDataFile',
            id=corpus_id,
            content={'file': f},
            encoding=apistar.client.encoders.MultiPartEncoder.media_type,
        )

    def send_xml(self, operation_id, body=None, **kwargs):
        """
        Perform a request with an XML body.

        :param str operation_id: An OpenAPI operation ID.
        :param body: The XML body.
        :type body: str, bytes or a file-like object opened in binary mode
        :param kwargs: Other arguments sent to :meth:`ArkindexClient.custom_request`.
        """

        if isinstance(body, FileIO):
            assert body.mode == 'rb', 'File-like objects should be opened in binary mode'

        return self.custom_request(
            operation_id,
            content=body,
            encoding=XMLEncoder.media_type,
            **kwargs,
        )
