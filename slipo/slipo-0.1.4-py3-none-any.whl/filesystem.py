"""
Client for accessing the user remote file system
"""

import os
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

API_BROWSE = 'api/{api_version}/file-system/'
API_DOWNLOAD = 'api/{api_version}/file-system/'
API_UPLOAD = 'api/{api_version}/file-system/upload/'


class FileSystemClient(object):
    """FileSystemClient provides methods for browsing, uploading and downloading
    files from the user remote file system.

    Details about the API responses are available at the `SLIPO`_ site.

    Args:
        base_url (str): Base URL for SLIPO API endpoints. The default
            value is ``https://app.dev.slipo.eu/``.
        api_key (str): SLIPO API key. An application key can be generated using
            the SLIPO Workbench application.

    Returns:
        A :py:class:`FileSystemClient <slipo.filesystem.FileSystemClient>` object.

    .. _SLIPO:
       https://app.dev.slipo.eu/docs/webapp-api/index.html#api-FileSystem
    """

    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key

        self.headers = {
            'X-API-Key': api_key
        }

    @json_response
    def browse(self) -> dict:
        """Browse all files and folders on the remote file system.

        Returns:
            A :obj:`dict` representing the parsed JSON response.

        Raises:
            SlipoException: If a network or server error has occurred.
        """

        endpoint = API_BROWSE.format(api_version=API_VERSION)
        url = urljoin(self.base_url, endpoint)

        return requests.get(url, headers=self.headers)

    @file_response('target')
    def download(self, source: str, target: str, overwrite: bool = False) -> None:
        """Download a file from the remote file system.

        Args:
            source (str): Relative file path on the remote file system.
            target (str): The path where to save the file.
            overwrite (bool, optional): Set true if the operation should
                overwrite any existing file.

        Raises:
            SlipoException: If a network, server error or I/O error has occurred.
        """

        if os.path.isfile(target) and not overwrite:
            raise SlipoException(
                'File {target} already exists'.format(target=target))

        if os.path.isdir(target):
            raise SlipoException(
                'Path {target} is a directory'.format(target=target))

        endpoint = API_DOWNLOAD.format(api_version=API_VERSION)
        url = urljoin(self.base_url, endpoint)

        params = {'path': source}

        return requests.get(url, headers=self.headers, params=params)

    @json_response
    def upload(self, source, target, overwrite=False) -> dict:
        """Upload a file to the remote file system.

        Note:
            File size constraints are enforced on the uploaded file. The default
            installation allows files up to 20 Mb. 

            Moreover, space quotas are applied on the server. The default user
            space is 5GB.

            Directory nesting constraints are applied for the ``target`` value. The
            default installation allows nesting of directories up to 5 levels.

        Args:
            source (str): The path of the file to upload.
            target (str): Relative path on the remote file system where to save the
                file. If the directory does not exist, it will be created.
            overwrite (bool, optional): Set true if the operation should overwrite
                any existing file.

        Raises:
            SlipoException: If a network, server error or I/O error has occurred.
        """

        # Configure endpoint
        endpoint = API_UPLOAD.format(api_version=API_VERSION)
        url = urljoin(self.base_url, endpoint)

        # Prepare request parameters
        path, filename = os.path.split(target)

        data = {
            'path': path,
            'filename': filename,
            'overwrite': overwrite,
        }

        files = {
            'data': (None, json.dumps(data), 'application/json'),
            'file': (os.path.basename(source), open(source, 'rb'), 'application/octet-stream'),
        }

        # Send request and check response
        return requests.post(url, headers=self.headers, files=files)
