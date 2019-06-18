from typing import Dict

from requests import Session, Response
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from mindfoundry.optaas.client.version_check import compare_versions, CLIENT_VERSION

DEFAULT_MAX_RETRIES = 3
RETRY_STATUS_CODES = [500, 501, 502, 503, 504]


class OPTaaSError(RuntimeError):
    """Wrapper class for an error :class:`.Response` received from OPTaaS."""

    def __init__(self, response: Response) -> None:
        self.status_code = response.status_code
        try:
            self.message = response.json()['message']
        except BaseException:
            self.message = response.content.decode() if response.content else ''
        super().__init__(f"Status: {self.status_code}  Message: {self.message}")


class OPTaaSResponse:
    """Wrapper class for a successful :class:`.Response` received from OPTaaS."""

    def __init__(self, response: Response, disable_version_check: bool = False) -> None:
        if not disable_version_check:
            compare_versions(response)
        if response.ok:
            self.body = response.json()
        else:
            raise OPTaaSError(response)


class OPTaaSSession:
    """Wrapper class for a :class:`.Session` that makes requests to OPTaaS.

    Args:
        server_url (str): URL of your OPTaaS server
        api_key (str): Your personal API key
        disable_version_check (bool, default False):
            Set to True if you don't want to be notified when a new version of the client is available
        max_retries (int, default 3): How many times to retry a request if a connection error occurs.
        keep_alive (bool, default True): Whether to set the `Connection` HTTP Header to "keep-alive".
    """

    def __init__(self, server_url: str, api_key: str, disable_version_check: bool, max_retries: int, keep_alive: bool) -> None:
        self._session = self._make_session(server_url, max_retries)
        self._root_url = server_url
        self._headers = {
            'X-ApiKey': api_key,
            'User-Agent': 'PythonClient/' + CLIENT_VERSION,
            'Connection': 'keep-alive' if keep_alive else 'close'
        }
        self._disable_version_check = disable_version_check

    @staticmethod
    def _make_session(server_url: str, max_retries: int) -> Session:
        session = Session()
        retry = Retry(total=max_retries, connect=max_retries, backoff_factor=0.5, method_whitelist=False,
                      status_forcelist=RETRY_STATUS_CODES)
        session.mount(server_url, HTTPAdapter(max_retries=retry))
        return session

    def post(self, endpoint: str, body: dict) -> OPTaaSResponse:
        """Make a POST request to OPTaaS with a JSON body.

        Args:
            endpoint (str): Endpoint for the request (will be appended to the server_url).
            body (dict): Request body in JSON format.

        Returns:
            The :class:`.OPTaaSResponse` to the request.

        Raises:
            :class:`.OPTaaSError` if an error response is received.
        """
        return OPTaaSResponse(self._session.post(self._root_url + endpoint, json=body, headers=self._headers),
                              disable_version_check=self._disable_version_check)

    def put(self, endpoint: str, body: dict) -> OPTaaSResponse:
        """Make a PUT request to OPTaaS with a JSON body.

        Args:
            endpoint (str): Endpoint for the request (will be appended to the server_url).
            body (dict): Request body in JSON format.

        Returns:
            The :class:`.OPTaaSResponse` to the request.

        Raises:
            :class:`.OPTaaSError` if an error response is received.
        """
        return OPTaaSResponse(self._session.put(self._root_url + endpoint, json=body, headers=self._headers),
                              disable_version_check=self._disable_version_check)

    def get(self, endpoint: str, query_params: Dict = None) -> OPTaaSResponse:
        """Make a GET request to OPTaaS

        Args:
            endpoint (str): Endpoint for the request (will be appended to the server_url).
            query_params (Dict, optional): Query parameters in Dict format (will be appended to the url).

        Returns:
            The :class:`.OPTaaSResponse` to the request.

        Raises:
            :class:`.OPTaaSError` if an error response is received.
        """
        return OPTaaSResponse(self._session.get(self._root_url + endpoint, headers=self._headers, params=query_params),
                              disable_version_check=self._disable_version_check)

    def delete(self, endpoint: str) -> OPTaaSResponse:
        """Make a DELETE request to OPTaaS

        Args:
            endpoint (str): Endpoint for the request (will be appended to the server_url).

        Returns:
            The :class:`.OPTaaSResponse` to the request.

        Raises:
            :class:`.OPTaaSError` if an error response is received.
        """
        return OPTaaSResponse(self._session.delete(self._root_url + endpoint, headers=self._headers),
                              disable_version_check=self._disable_version_check)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self._root_url == other._root_url  # pylint: disable=protected-access
