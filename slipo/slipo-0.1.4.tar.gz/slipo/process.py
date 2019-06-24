"""
Client for managing existing POI data integration workflows
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

API_QUERY = '/api/{api_version}/process/'
API_STATUS = '/api/{api_version}/process/{id}/{version}/'
API_DOWNLOAD = '/api/{api_version}/process/{id}/{version}/file/{fileId}'
API_START = '/api/{api_version}/process/{id}/{version}/start'
API_STOP = '/api/{api_version}/process/{id}/{version}/stop'


class ProcessClient(object):
    """ProcessClient provides methods for managing existing POI data integration
    workflows.

    Details about the API responses are available at the `SLIPO`_ site.

    Args:
        base_url (str): Base URL for SLIPO API endpoints. The default
            value is ``https://app.dev.slipo.eu/``.
        api_key (str): SLIPO API key. An application key can be generated using
            the SLIPO Workbench application.

    Returns:
        A :py:class:`ProcessClient <slipo.process.ProcessClient>` object.

    .. _SLIPO:
       https://app.dev.slipo.eu/docs/webapp-api/index.html#api-Workflow
    """

    def __init__(self, base_url, api_key):
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
        """Query workflow instances.

        Args:
            term (str, optional): A term for filtering workflows. If specified, 
                only the workflows whose name contains the term are returned.
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

    @json_response
    def start(self, process_id: int, process_version: int) -> None:
        """Start or resume the execution of a workflow instance.

        Args:
            process_id (int): The process id.
            process_version (int): The process revision.

        Raises:
            SlipoException: If a network or server error has occurred.
        """

        endpoint = API_START.format(
            api_version=API_VERSION,
            id=process_id,
            version=process_version,
        )
        url = urljoin(self.base_url, endpoint)

        return requests.post(url, headers=self.content_headers)

    @json_response
    def stop(self, process_id: int, process_version: int) -> None:
        """Stop a running workflow execution instance.

        Args:
            process_id (int): The process id.
            process_version (int): The process revision.

        Raises:
            SlipoException: If a network or server error has occurred.
        """

        endpoint = API_STOP.format(
            api_version=API_VERSION,
            id=process_id,
            version=process_version,
        )
        url = urljoin(self.base_url, endpoint)

        return requests.post(url, headers=self.content_headers)

    @json_response
    def status(self, process_id: int, process_version: int) -> dict:
        """Check the status of a workflow execution instance.

        Args:
            process_id (int): The process id.
            process_version (int): The process revision.

        Returns:
            A :obj:`dict` representing the parsed JSON response.

        Raises:
            SlipoException: If a network or server error has occurred.
        """

        endpoint = API_STATUS.format(
            api_version=API_VERSION,
            id=process_id,
            version=process_version,
        )
        url = urljoin(self.base_url, endpoint)

        return requests.get(url, headers=self.content_headers)

    @file_response('target')
    def download(self, process_id: int, process_version: int, file_id: int, target: str) -> None:
        """Download an input or output file for a specific workflow execution instance.

        During the execution of a workflow the following file types may be created:
            - ``CONFIGURATION``: Tool configuration
            - ``INPUT``: Input file
            - ``OUTPUT``: Output file
            - ``SAMPLE``: Sample data collected during step execution
            - ``KPI``: Tool specific or aggregated KPI data
            - ``QA``: Tool specific QA data
            - ``LOG``: Logs recorded during step execution 

        Args:
            process_id (int): The process id.
            process_version (int): The process revision.
            file_id (int): The file id.
            target (str): The path where to save the file.

        Raises:
            SlipoException: If a network, server error or I/O error has occurred.
        """

        endpoint = API_DOWNLOAD.format(
            api_version=API_VERSION,
            id=process_id,
            version=process_version,
            fileId=file_id,
        )

        url = urljoin(self.base_url, endpoint)

        return requests.get(url, headers=self.auth_headers)
