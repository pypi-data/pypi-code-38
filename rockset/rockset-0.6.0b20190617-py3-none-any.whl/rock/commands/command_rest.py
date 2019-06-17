import requests
import rockset

from .command import Command
from rockset.exception import HTTPError, RequestTimeout, InputError


class RESTCommand(Command):
    def __init__(self, *args, **kwargs):
        super(RESTCommand, self).__init__(*args, **kwargs)
        self.require_creds()
        self.logger.info('target api_server: {}'.format(self.api_server))
        self.logger.info('target api_key: {}'.format(self.api_key_masked))

    def _url(self, url):
        return '{}{}'.format(self.api_server, url)

    def _headers(self, headers):
        if headers is None:
            headers = {}
        headers.update(
            {
                'Authorization': 'ApiKey {}'.format(self.api_key),
                'x-rockset-version': rockset.version(),
                'User-Agent': 'python',
            }
        )
        return headers

    def _exception(self, response):
        return HTTPError(code=response.status_code, message=response.reason)

    def _apicall(self, method, url, *args, **kwargs):
        return method(url, *args, **kwargs)

    def _method(self, method, url, *args, **kwargs):
        kwargs['timeout'] = kwargs.get('timeout', 10)
        kwargs['headers'] = self._headers(kwargs.get('headers'))
        try:
            response = self._apicall(method, self._url(url), *args, **kwargs)
            if response.status_code != 200:
                raise self._exception(response)
            return response.json()
        except requests.exceptions.ConnectionError as e:
            message = 'error connecting to {}'.format(self.api_server)
            raise RequestTimeout(message=message, timeout=None) from None
        except requests.exceptions.RequestException as e:
            raise InputError(
                code='-', message=str(e), type='InputError'
            ) from None

    def post(self, url, *args, **kwargs):
        return self._method(requests.post, url, *args, **kwargs)

    def get(self, url, *args, **kwargs):
        return self._method(requests.get, url, *args, **kwargs)
