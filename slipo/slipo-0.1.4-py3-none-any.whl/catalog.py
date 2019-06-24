"""
Client for accessing the resource catalog
"""

import json
import http
import requests

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

from .exceptions import SlipoException
from .utils import json_response, file_response

API_VERSION = "v1"

API_QUERY = 'api/{api_version}/resource/'
API_DOWNLOAD = '/api/{api_version}/resource/{id}/{version}/'


class CatalogClient(object):
    """CatalogClient provides methods for querying the resource catalog and
    downloading RDF datasets. All datasets are encoded in `N-Triples` format.

    Details about the API responses are available at the `SLIPO`_ site.

    Args:
        base_url (str): Base URL for SLIPO API endpoints. The default
            value is ``https://app.dev.slipo.eu/``.
        api_key (str): SLIPO API key. An application key can be generated using
            the SLIPO Workbench application.

    Returns:
        A :py:class:`CatalogClient <slipo.catalog.CatalogClient>` object.

    .. _SLIPO:
       https://app.dev.slipo.eu/docs/webapp-api/index.html#api-Resources
    """

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key

        self.auth_headers = {
            'X-API-Key': api_key,
        }

        self.content_headers = {
            'X-API-Key': api_key,
            'Content-type': 'application/json',
        }

    @json_response
    def query(self, term: str = None, pageIndex: int = 0, pageSize: int = 10) -> dict:
        """Query resource catalog for RDF datasets.

        Args:
            term (str, optional): A term for filtering resources. If specified, 
                only the resources whose name contains the term are returned.
            pageIndex (str, optional): Page index for data pagination.
            pageSize (str, optional): Page size for data pagination.

        Returns:
            A :obj:`dict` representing the parsed JSON response.
        
        Raises:
            SlipoException: If a network or server error has occurred.
        """

        endpoint = API_QUERY.format(api_version=API_VERSION)
        url = urljoin(self.base_url, endpoint)

        query = {
            'pagingOptions': {
                'pageIndex': pageIndex,
                'pageSize': pageSize,
            },
            'query': {
                'name': term,
            },
        }

        return requests.post(
            url,
            headers=self.content_headers,
            data=json.dumps(query)
        )

    @file_response('target')
    def download(self, resource_id: int, resource_version: int, target: str) -> None:
        """Download a resource to the local file system

        Args:
            resource_id (int): The resource id.
            resource_version (int): The resource revision.
            target (str): The path where to save the file.

        Raises:
            SlipoException: If a network, server error or I/O error has occurred.
        """

        endpoint = API_DOWNLOAD.format(
            api_version=API_VERSION,
            id=resource_id,
            version=resource_version,
        )

        url = urljoin(self.base_url, endpoint)

        return requests.get(url, headers=self.auth_headers)
