import json
import logging
import time

import requests

try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse


class CommunicationObject(object):

    def __init__(self, url, project_id, token, timeout=900.0, chunk_size=256, verify=True, critical=False):
        """
        Communications with the platform

        Parameters
        ----------
        url : str
            Platform URL
        project_id : int
            Unique project identifier
        token : str
            Unique token that authenticates the communication
        timeout : float or tuple, optional
            How many seconds to wait for the server to send data before giving up, as a float, or a
            (connect timeout, read timeout) tuple. Defaults to
        chunk_size : int
            Size of chunks in bytes (1MB = 1024KB, 1KB = 1024B)
        verify : bool, optional
            Controls whether the server's TLS certificate is verified.
            Defaults to True.
        critical: bool, optional
            Overrides total_retry seting in requests by making themm fail after the first error if set.
        """
        self.timeout = timeout
        self.chunk_size = chunk_size

        self.__req_url = url
        self.__project_id = project_id
        self.__token = token
        self.__verify = verify
        self.__critical = critical

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        ret = self.send_request("logout")
        if not ret['success']:
            # Not being able to logout is a security issue and must be a fatal error
            raise RuntimeError('Unable to logout')

    def send_request(self, access_point, req_data=None, req_headers=None, return_json=True, timeout=None,
                     total_retry=5, stream=False, **kwargs):
        """
        Send a POST request to the platform to the given API endpoint.

        Parameters
        ----------
        access_point : str
            API endpoint. Will be joined with the request URL provided at construction time to create the
            full ("absolute") url
        req_data : dict or str, optional
            Request data
        req_headers : dict, optional
            Request headers
        return_json : bool, optional
            Whether the response should be a JSON object or a requests.Response instance.
            Defaults to True.
        timeout : float, optional
            Timeout in seconds for this request.
            Defaults to the timeout set at construction time.
        total_retry : int, optional
            Number of connection retries.
            Defaults to 5.
        stream : bool, optional
            If False, the response content will be immediately downloaded.
        kwargs : dict
            Additional arguments to be passed to `requests.post`

        Returns
        -------
        requests.Response or dict
            JSON response encoded in a dictionary if return_json is True (default),
            otherwise requests.Response object.
        """
        logger = logging.getLogger(__name__)

        # Default parameters
        req_data = req_data or dict()
        req_headers = req_headers or dict()
        timeout = timeout or self.timeout

        # Add authentication for the platform
        req_headers["Cookie"] = "AUTH_COOKIE={}; MINT_AP={}".format(self.__token, self.__project_id)
        req_headers["Mint-Api-Call"] = "1"

        url = urlparse.urljoin(self.__req_url, access_point)
        retry_counter = 0
        while True:
            try:
                response = requests.post(
                    url,
                    data=req_data,
                    headers=req_headers,
                    timeout=timeout,
                    verify=self.__verify,
                    stream=stream,
                    **kwargs
                )

                # log & raise error if we get a HTTP error code
                if not response.ok:
                    logger.debug('{!r} HTTP response: {!r}'.format(url, response.text))
                response.raise_for_status()

            except (requests.HTTPError, requests.Timeout, requests.ConnectionError):
                retry_counter += 1
                if self.__critical or total_retry == retry_counter:
                    raise
                time.sleep(retry_counter * 5)

            else:
                return json.loads(response.text) if return_json else response

    def send_files(self, access_point, files, req_data=None, req_headers=None, return_json=True, timeout=None,
                   total_retry=5, stream=False, **kwargs):
        """
        Send a POST request to the platform to the given API endpoint.

        Parameters
        ----------
        access_point : str
            API endpoint. Will be joined with the request URL provided at construction time to create the
            full ("absolute") url
        files : dict
            Request files
        req_data : dict or str, optional
            Request data
        req_headers : dict, optional
            Request headers
        return_json : bool, optional
            Whether the response should be a JSON object or a requests.Response instance.
            Defaults to True.
        timeout : float, optional
            Timeout in seconds for this request.
            Defaults to the timeout set at construction time.
        total_retry : int, optional
            Number of connection retries.
            Defaults to 5.
        stream : bool, optional
            If False, the response content will be immediately downloaded.
        kwargs : dict
            Additional arguments to be passed to `requests.post`

        Returns
        -------
        requests.Response or dict
            JSON response encoded in a dictionary if return_json is True (default),
            otherwise requests.Response object.
        """
        logger = logging.getLogger(__name__)

        # Default parameters
        req_data = req_data or dict()
        req_headers = req_headers or dict()
        timeout = timeout or self.timeout

        # Add authentication for the platform
        req_headers["Cookie"] = "AUTH_COOKIE={}; MINT_AP={}".format(self.__token, self.__project_id)
        req_headers["Mint-Api-Call"] = "1"

        retry_counter = 0
        while True:
            try:
                url = urlparse.urljoin(self.__req_url, access_point)
                response = requests.post(
                    url,
                    files=files,
                    data=req_data,
                    headers=req_headers,
                    timeout=timeout,
                    verify=self.__verify,
                    stream=stream,
                    **kwargs
                )

                # Raise error if we get a HTTP error code
                response.raise_for_status()
                result = json.loads(response.text) if return_json else response
                logger.info('{!r} HTTP response: {!r}'.format(url, result))
                return result

            except (requests.HTTPError, requests.Timeout, requests.ConnectionError):
                retry_counter += 1
                if self.__critical or total_retry == retry_counter:
                    raise
                time.sleep(retry_counter * 5)


class DummyCommunicationObject(object):
    def __init__(self, url, chunk_size=1):
        self.__req_url = url
        self.chunk_size = chunk_size
        self.mock_response = None
        self.sent_contents = None

    def send_request(self, access_point, *args, **kwargs):
        self.sent_contents = args[0]
        if self.mock_response is None:
            return DummmyResponse()
        else:
            return self.mock_response


class DummmyResponse(object):
    def iter_content(self, *args, **kwargs):
        return []
