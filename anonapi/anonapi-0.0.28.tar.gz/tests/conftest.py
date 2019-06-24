"""Conftest.py is loaded for each pytest. Contains fixtures shared by multiple tests, amongs other things """
from _pytest.fixtures import fixture

from anonapi.client import WebAPIClient
from tests.factories import RequestsMock


@fixture
def mocked_requests_client():
    """A WebAPIClient instance that does not actually do http calls but uses mocked responses

    Returns
    -------
    (WebAPIClient, RequestsMock)
        client with mocked requests lib, and te mocked requests lib itself

    """
    client = WebAPIClient(hostname="test.host", username="testuser", token="token")

    requests_mock = RequestsMock()
    client.requestslib = requests_mock
    return client, requests_mock


