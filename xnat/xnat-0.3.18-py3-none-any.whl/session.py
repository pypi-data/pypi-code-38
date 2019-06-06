# Copyright 2011-2015 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import
from __future__ import unicode_literals
import datetime
import io
import netrc
import os
import re
import threading

from progressbar import AdaptiveETA, AdaptiveTransferSpeed, Bar, BouncingBar, \
    DataSize, Percentage, ProgressBar, Timer, UnknownLength
import requests
import six
from six.moves.urllib import parse

from . import exceptions
from .core import XNATListing, caching
from .inspect import Inspect
from .prearchive import Prearchive
from .users import Users
from .services import Services
from .exceptions import XNATValueError

try:
    FILE_TYPES = (file, io.IOBase)
except NameError:
    FILE_TYPES = io.IOBase


class XNATSession(object):
    """
    The main XNATSession session class. It keeps a connection to XNATSession alive and
    manages the main communication to XNATSession. To keep the connection alive
    there is a background thread that sends a heart-beat to avoid a time-out.

    The main starting points for working with the XNATSession server are:

    * :py:meth:`XNATSession.projects <xnat.session.XNATSession.projects>`
    * :py:meth:`XNATSession.subjects <xnat.session.XNATSession.subjects>`
    * :py:meth:`XNATSession.experiments <xnat.session.XNATSession.experiments>`
    * :py:meth:`XNATSession.prearchive <xnat.session.XNATSession.prearchive>`
    * :py:meth:`XNATSession.services <xnat.session.XNATSession.services>`
    * :py:meth:`XNATSession.users <xnat.session.XNATSession.users>`

    .. note:: Some methods create listing that are using the :py:class:`xnat.core.XNATListing <xnat.core.XNATListing>`
              class. They allow for indexing with both XNATSession ID and a secondary key (often the
              label). Also they support basic filtering and tabulation.

    There are also methods for more low level communication. The main methods
    are :py:meth:`XNATSession.get <xnat.session.XNATSession.get>`, :py:meth:`XNATSession.post <xnat.session.XNATSession.post>`,
    :py:meth:`XNATSession.put <xnat.session.XNATSession.put>`, and :py:meth:`XNATSession.delete <xnat.session.XNATSession.delete>`.
    The methods do not query URIs but instead query XNATSession REST paths as described in the
    `XNATSession 1.6 REST API Directory <https://wiki.xnat.org/display/XNAT16/XNATSession+REST+API+Directory>`_.

    For an even lower level interfaces, the :py:attr:`XNATSession.interface <xnat.session.XNATSession.interface>`
    gives access to the underlying `requests <https://requests.readthedocs.org>`_ interface.
    This interface has the user credentials and benefits from the keep alive of this class.

    .. note:: :py:class:`XNATSession <xnat.session.XNATSession>` Objects have a client-side cache. This is for efficiency, but might cause
              problems if the server is being changed by a different client. It is possible
              to clear the current cache using :py:meth:`XNATSession.clearcache <xnat.session.XNATSession.clearcache>`.
              Turning off caching complete can be done by setting
              :py:attr:`XNATSession.caching <xnat.session.XNATSession.caching>`.

    .. warning:: You should NOT try use this class directly, it should only
                 be created by :py:func:`xnat.connect <xnat.connect>`.
    """

    def __init__(self, server, logger, interface=None, user=None,
                 password=None, keepalive=None, debug=False,
                 original_uri=None, logged_in_user=None):
        # Class lookup to populate (session specific, as all session have their
        # own classes based on the server xsd)
        self.XNAT_CLASS_LOOKUP = {}

        self.classes = None
        self._interface = interface
        self._projects = None
        self._server = parse.urlparse(server) if server else None
        if original_uri is not None:
            self._original_uri = original_uri.rstrip('/')
        else:
            self._original_uri = server.rstrip('/')
        self._logged_in_user = logged_in_user
        self._cache = {'__objects__': {}}
        self.caching = True
        self._source_code_file = None
        self._services = Services(xnat_session=self)
        self._prearchive = Prearchive(xnat_session=self)
        self._users = Users(xnat_session=self)
        self._debug = debug
        self.logger = logger
        self.inspect = Inspect(self)
        self.request_timeout = None

        # Accepted status
        self.accepted_status_get = [200]
        self.accepted_status_post = [200, 201]
        self.accepted_status_put = [200, 201]
        self.accepted_status_delete = [200]
        self.skip_response_check = False
        self.skip_response_content_check = False

        session_expiration = self.session_expiration_time
        if session_expiration is not None:
            # 30 seconds before the expiration, at most once per 10 seconds
            if session_expiration[1] < 30:
                self.logger.warning(
                    ('Server session expiration time ({}) is lower than 30 seconds,'
                     ' setting heartbeat interval to the minimum of 10 seconds.').format(session_expiration[1]))
            default_keepalive = max(session_expiration[1] - 20, 10)
        else:
            default_keepalive = 14 * 60  # Default to 14 minutes

        # Set the keep alive settings and spawn the keepalive thread for sending heartbeats
        if keepalive is None or keepalive is True:
            keepalive = default_keepalive

        if isinstance(keepalive, int) and keepalive > 0:
            self._keepalive = True
            self._keepalive_interval = keepalive
        else:
            self._keepalive = False
            self._keepalive_interval = default_keepalive  # Not used while keepalive is false, but set a default

        self._keepalive_running = False
        self._keepalive_thread = None
        self._keepalive_event = threading.Event()

        # If needed connect here
        self.connect(server=server, user=user, password=password)

    def __del__(self):
        self.disconnect()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def connect(self, server=None, user=None, password=None):
        # If not connected, connect now
        if self.interface is None:
            if server is None:
                raise ValueError('Cannot connect if no server is given')
            self.logger.info('Connecting to server {}'.format(server))
            if self._interface is not None:
                self.disconnect()

            self._server = parse.urlparse(server)

            if user is None and password is None:
                self.logger.info('Retrieving login info for {}'.format(self._server.netloc))
                try:
                    user, _, password = netrc.netrc().authenticators(self._server.netloc)
                except TypeError:
                    raise ValueError('Could not retrieve login info for "{}" from the .netrc file!'.format(server))

            self._interface = requests.Session()
            if (user is not None) or (password is not None):
                self._interface.auth = (user, password)

        # Create a keepalive thread
        self._keepalive_running = True
        self._keepalive_thread = threading.Thread(target=self._keepalive_thread_run)
        self._keepalive_thread.daemon = True  # Make sure thread stops if program stops
        self._keepalive_thread.start()
        self.heartbeat()  # Make sure the heartbeat is given and there is no chance of timeout

    def disconnect(self):
        # Stop the keepalive thread
        self._keepalive_running = False
        self._keepalive_event.set()

        if self._keepalive_thread is not None:
            if self._keepalive_thread.is_alive():
                self._keepalive_thread.join(3.0)
            self._keepalive_thread = None

        # Kill the session
        if self._server is not None and self._interface is not None:
            self.delete('/data/JSESSION', headers={'Connection': 'close'})

        # Set the server and interface to None
        self._interface = None
        self._server = None

        # If this object is created using an automatically generated file
        # we have to remove it.
        if self._source_code_file is not None:
            source_pyc = self._source_code_file + 'c'
            if os.path.isfile(self._source_code_file):
                os.remove(self._source_code_file)
                self._source_code_file = None
            if os.path.isfile(source_pyc):
                os.remove(source_pyc)

        self.classes = None

    @property
    def keepalive(self):
        return self._keepalive

    @keepalive.setter
    def keepalive(self, value):
        if isinstance(value, int):
            if value > 0:
                self._keepalive_interval = value
                value = True
            else:
                value = False

        elif not isinstance(value, bool):
            raise TypeError('Type should be an integer or boolean!')

        self._keepalive = value

        if self.keepalive:
            # Send a new heartbeat and restart the timer to make sure the interval is correct
            self._keepalive_event.set()
            self.heartbeat()

    def heartbeat(self):
        self.get('/data/JSESSION')

    def _keepalive_thread_run(self):
        # This thread runs until the program stops, it should be inexpensive if not used due to the long sleep time
        while self._keepalive_running:
            # Wait returns False on timeout and True otherwise
            if not self._keepalive_event.wait(self._keepalive_interval):
                if self.keepalive:
                    self.heartbeat()
            else:
                self._keepalive_event.clear()

    @property
    def logged_in_user(self):
        return self._logged_in_user

    @property
    def debug(self):
        return self._debug

    @property
    def interface(self):
        """
        The underlying `requests <https://requests.readthedocs.org>`_ interface used.
        """
        return self._interface

    @property
    def uri(self):
        return '/data/archive'

    @property
    def fulluri(self):
        return self.uri

    @property
    def xnat_session(self):
        return self

    @property
    def session_expiration_time(self):
        """
        Get the session expiration time information from the cookies. This
        returns the timestamp (datetime format) when the session was created
        and an integer with the session timeout interval.

        This can return None if the cookie is not found or cannot be parsed.

        :return: datetime with last session refresh and integer with timeout in seconds
        :rtype: tuple
        """
        expiration_string = self.interface.cookies.get('SESSION_EXPIRATION_TIME')

        if expiration_string is None:
            return

        match = re.match(r'^"(?P<timestamp>\d+),(?P<interval>\d+)"$', expiration_string)
        if match is None:
            self.logger.warning('Could not parse SESSION_EXPIRATION_TIME cookie')
            return None

        session_timestamp = datetime.datetime.fromtimestamp(int(match.group('timestamp')) / 1000)
        expiration_interval = int(match.group('interval')) / 1000
        return session_timestamp, expiration_interval

    def _check_response(self, response, accepted_status=None, uri=None):
        if self.debug:
            self.logger.debug('Received response with status code: {}'.format(response.status_code))

        if not self.skip_response_check:
            if accepted_status is None:
                accepted_status = [200, 201, 202, 203, 204, 205, 206]  # All successful responses of HTML
            if response.status_code not in accepted_status or (not self.skip_response_content_check and response.text.startswith(('<!DOCTYPE', '<html>'))):
                raise exceptions.XNATResponseError('Invalid response from XNATSession for url {} (status {}):\n{}'.format(uri, response.status_code, response.text))

    def get(self, path, format=None, query=None, accepted_status=None, timeout=None, headers=None):
        """
        Retrieve the content of a given REST directory.

        :param str path: the path of the uri to retrieve (e.g. "/data/archive/projects")
                         the remained for the uri is constructed automatically
        :param str format: the format of the request, this will add the format= to the query string
        :param dict query: the values to be added to the query string in the uri
        :param list accepted_status: a list of the valid values for the return code, default [200]
        :param timeout: timeout in seconds, float or (connection timeout, read timeout)
        :type timeout: float or tuple
        :param dict headers: the HTTP headers to include
        :returns: the requests reponse
        :rtype: requests.Response
        """
        accepted_status = accepted_status or self.accepted_status_get
        uri = self._format_uri(path, format, query=query)
        timeout = timeout or self.request_timeout

        self.logger.debug('GET URI {}'.format(uri))

        try:
            response = self.interface.get(uri, timeout=timeout, headers=headers)
        except requests.exceptions.SSLError:
            raise exceptions.XNATSSLError('Encountered a problem with the SSL connection, are you sure the server is offering https?')
        self._check_response(response, accepted_status=accepted_status, uri=uri)  # Allow OK, as we want to get data
        return response

    def head(self, path, accepted_status=None, allow_redirects=False, timeout=None, headers=None):
        """
        Retrieve the header for a http request of a given REST directory.

        :param str path: the path of the uri to retrieve (e.g. "/data/archive/projects")
                         the remained for the uri is constructed automatically
        :param list accepted_status: a list of the valid values for the return code, default [200]
        :param bool allow_redirects: allow you request to be redirected
        :param timeout: timeout in seconds, float or (connection timeout, read timeout)
        :type timeout: float or tuple
        :param dict headers: the HTTP headers to include
        :returns: the requests reponse
        :rtype: requests.Response
        """
        accepted_status = accepted_status or self.accepted_status_get
        uri = self._format_uri(path)
        timeout = timeout or self.request_timeout

        self.logger.debug('GET URI {}'.format(uri))

        try:
            response = self.interface.head(uri, allow_redirects=allow_redirects, timeout=timeout, headers=headers)
        except requests.exceptions.SSLError:
            raise exceptions.XNATSSLError('Encountered a problem with the SSL connection, are you sure the server is offering https?')
        self._check_response(response, accepted_status=accepted_status, uri=uri)  # Allow OK, as we want to get data
        return response

    def post(self, path, data=None, json=None, format=None, query=None, accepted_status=None, timeout=None, headers=None):
        """
        Post data to a given REST directory.

        :param str path: the path of the uri to retrieve (e.g. "/data/archive/projects")
                         the remained for the uri is constructed automatically
        :param data: Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
        :param json: json data to send in the body of the :class:`Request`.
        :param str format: the format of the request, this will add the format= to the query string
        :param dict query: the values to be added to the query string in the uri
        :param list accepted_status: a list of the valid values for the return code, default [200, 201]
        :param timeout: timeout in seconds, float or (connection timeout, read timeout)
        :type timeout: float or tuple
        :param dict headers: the HTTP headers to include
        :returns: the requests reponse
        :rtype: requests.Response
        """
        accepted_status = accepted_status or self.accepted_status_post
        uri = self._format_uri(path, format, query=query)
        timeout = timeout or self.request_timeout

        self.logger.debug('POST URI {}'.format(uri))
        if self.debug:
            self.logger.debug('POST DATA {}'.format(data))

        try:
            response = self._interface.post(uri, data=data, json=json, timeout=timeout, headers=headers)
        except requests.exceptions.SSLError:
            raise exceptions.XNATSSLError('Encountered a problem with the SSL connection, are you sure the server is offering https?')
        self._check_response(response, accepted_status=accepted_status, uri=uri)
        return response

    def put(self, path, data=None, files=None, json=None, format=None, query=None, accepted_status=None, timeout=None, headers=None):
        """
        Put the content of a given REST directory.

        :param str path: the path of the uri to retrieve (e.g. "/data/archive/projects")
                         the remained for the uri is constructed automatically
        :param data: Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
        :param json: json data to send in the body of the :class:`Request`.
        :param files: Dictionary of ``'name': file-like-objects`` (or ``{'name': file-tuple}``) for multipart encoding upload.
                      ``file-tuple`` can be a 2-tuple ``('filename', fileobj)``, 3-tuple ``('filename', fileobj, 'content_type')``
                      or a 4-tuple ``('filename', fileobj, 'content_type', custom_headers)``, where ``'content-type'`` is a string
                      defining the content type of the given file and ``custom_headers`` a dict-like object containing additional headers
                      to add for the file.
        :param str format: the format of the request, this will add the format= to the query string
        :param dict query: the values to be added to the query string in the uri
        :param list accepted_status: a list of the valid values for the return code, default [200, 201]
        :param timeout: timeout in seconds, float or (connection timeout, read timeout)
        :type timeout: float or tuple
        :param dict headers: the HTTP headers to include
        :returns: the requests reponse
        :rtype: requests.Response
        """
        accepted_status = accepted_status or self.accepted_status_put
        uri = self._format_uri(path, format, query=query)
        timeout = timeout or self.request_timeout

        self.logger.debug('PUT URI {}'.format(uri))
        if self.debug:
            self.logger.debug('PUT DATA {}'.format(data))
            self.logger.debug('PUT FILES {}'.format(data))

        try:
            response = self._interface.put(uri, data=data, files=files, json=json, timeout=timeout, headers=headers)
        except requests.exceptions.SSLError:
            raise exceptions.XNATSSLError('Encountered a problem with the SSL connection, are you sure the server is offering https?')
        self._check_response(response, accepted_status=accepted_status, uri=uri)  # Allow created OK or Create status (OK if already exists)
        return response

    def delete(self, path, headers=None, accepted_status=None, query=None, timeout=None):
        """
        Delete the content of a given REST directory.

        :param str path: the path of the uri to retrieve (e.g. "/data/archive/projects")
                         the remained for the uri is constructed automatically
        :param dict headers: the HTTP headers to include
        :param dict query: the values to be added to the query string in the uri
        :param list accepted_status: a list of the valid values for the return code, default [200]
        :param timeout: timeout in seconds, float or (connection timeout, read timeout)
        :type timeout: float or tuple
        :returns: the requests reponse
        :rtype: requests.Response
        """
        accepted_status = accepted_status or self.accepted_status_delete
        uri = self._format_uri(path, query=query)
        timeout = timeout or self.request_timeout

        self.logger.debug('DELETE URI {}'.format(uri))
        if self.debug:
            self.logger.debug('DELETE HEADERS {}'.format(headers))

        try:
            response = self.interface.delete(uri, headers=headers, timeout=timeout)
        except requests.exceptions.SSLError:
            raise exceptions.XNATSSLError('Encountered a problem with the SSL connection, are you sure the server is offering https?')
        self._check_response(response, accepted_status=accepted_status, uri=uri)
        return response

    def _format_uri(self, path, format=None, query=None, scheme=None):
        if path[0] != '/':

            if self._original_uri is not None and path.startswith(self._original_uri):
                path = path[len(self._original_uri):]  # Strip original uri

            if path[0] != '/':
                raise XNATValueError('The requested URI path should start with a / (e.g. /data/projects), found {}'.format(path))

        if query is None:
            query = {}

        if format is not None:
            query['format'] = format

        # Sanitize unicode in query
        if six.PY2:
            query = {k: v.encode('utf-8', 'xmlcharrefreplace') if isinstance(v, unicode) else v for k, v in query.items()}

        # Create the query string
        if len(query) > 0:
            query_string = parse.urlencode(query, doseq=True)
        else:
            query_string = ''

        data = (scheme or self._server.scheme,
                self._server.netloc,
                self._server.path.rstrip('/') + path,
                '',
                query_string,
                '')

        return parse.urlunparse(data)

    def url_for(self, obj, query=None, scheme=None):
        """
        Return the (external) url for a given XNAT object
        :param XNATBaseObject obj: object to get url for
        :param query: extra query string parameters
        :param scheme: scheme to use (when not using original url scheme)
        :return: external url for the object
        """
        return self._format_uri(obj.fulluri, query=query, scheme=scheme)

    def get_json(self, uri, query=None, accepted_status=None):
        """
        Helper function that perform a GET, but sets the format to JSON and
        parses the result as JSON

        :param str uri: the path of the uri to retrieve (e.g. "/data/archive/projects")
                         the remained for the uri is constructed automatically
        :param dict query: the values to be added to the query string in the uri
        """
        response = self.get(uri, format='json', query=query, accepted_status=accepted_status)
        try:
            return response.json()
        except ValueError:
            raise ValueError('Could not decode JSON from [{}] {}'.format(uri, response.text))

    def download_stream(self, uri, target_stream, format=None, verbose=False, chunk_size=524288, update_func=None, timeout=None):
        """
        Download the given ``uri`` to the given ``target_stream``.

        :param str uri:            Path of the uri to retrieve.
        :param file target_stream: A writable file-like object to save the
                                   stream to.
        :param str format:         Request format
        :param bool verbose:       If ``True``, and an ``update_func`` is not
                                   specified, a progress bar is shown on
                                   stdout.
        :param int chunk_size:     Download this many bytes at a time
        :param func update_func:   If provided, will be called every
                                   ``chunk_size`` bytes. Must accept three
                                   parameters:

                                     - the number of bytes downloaded so far
                                     - the total number of bytse to be
                                       downloaded (might be ``None``),
                                     - A boolean flag which is ``False`` during
                                       the download, and ``True`` when the
                                       download has completed (or failed)
        :param timeout: timeout in seconds, float or (connection timeout, read timeout)
        :type timeout: float or tuple
        """

        uri = self._format_uri(uri, format=format)
        self.logger.debug('DOWNLOAD STREAM {}'.format(uri))

        # Stream the get and write to file
        response = self.interface.get(uri, stream=True, timeout=timeout)

        if response.status_code not in self.accepted_status_get:
            raise exceptions.XNATResponseError('Invalid response from XNATSession for url {} (status {}):\n{}'.format(uri, response.status_code, response.text))

        # Get the content length if available
        content_length = response.headers.get('Content-Length', None)

        if isinstance(content_length, six.string_types):
            content_length = int(content_length)

        if verbose and update_func is None:
            update_func = default_update_func(content_length)
        if update_func is None:
            update_func = lambda *args: None

        if verbose:
            self.logger.info('Downloading {}:'.format(uri))

        bytes_read = 0
        try:
            update_func(0, content_length, False)
            for chunk in response.iter_content(chunk_size):
                if bytes_read == 0 and chunk[0] == '<' and chunk.startswith(('<!DOCTYPE', '<html>')):
                    raise ValueError('Invalid response from XNATSession (status {}):\n{}'.format(response.status_code, chunk))

                bytes_read += len(chunk)
                target_stream.write(chunk)

                update_func(bytes_read, content_length, False)
        finally:
            update_func(bytes_read, content_length, True)

    def download(self, uri, target, format=None, verbose=True, timeout=None):
        """
        Download uri to a target file
        """
        with open(target, 'wb') as out_fh:
            self.download_stream(uri, out_fh, format=format, verbose=verbose, timeout=timeout)

        if verbose:
            self.logger.info('\nSaved as {}...'.format(target))

    def download_zip(self, uri, target, verbose=True, timeout=None):
        """
        Download uri to a target zip file
        """
        self.download(uri, target, format='zip', verbose=verbose, timeout=timeout)

    def upload(self, uri, file_, retries=1, query=None, content_type=None, method='put', overwrite=False, timeout=None):
        """
        Upload data or a file to XNAT

        :param str uri: uri to upload to
        :param file_: the file handle, path to a file or a string of data
                      (which should not be the path to an existing file!)
        :param int retries: amount of times xnatpy should retry in case of
                            failure
        :param dict query: extra query string content
        :param content_type: the content type of the file, if not given it will
                             default to ``application/octet-stream``
        :param str method: either ``put`` (default) or ``post``
        :param bool overwrite: indicate if previous data should be overwritten
        :param timeout: timeout in seconds, float or (connection timeout, read timeout)
        :type timeout: float or tuple
        :return:
        """
        if overwrite:
            if query is None:
                query = {}
            query['overwrite'] = 'true'

        uri = self._format_uri(uri, query=query)
        self.logger.debug('UPLOAD URI {}'.format(uri))
        attempt = 0
        file_handle = None
        opened_file = False

        try:
            while attempt < retries:
                if isinstance(file_, FILE_TYPES):
                    # File is open file handle, seek to 0
                    file_handle = file_
                    file_.seek(0)
                # Make sure conditions are valid for os.path.isfile to function
                elif isinstance(file_, six.string_types) and '\0' not in file_ and os.path.isfile(file_):
                    # File is str path to file
                    file_handle = open(file_, 'rb')
                    opened_file = True
                else:
                    # File is data to upload
                    file_handle = file_

                attempt += 1

                try:
                    # Set the content type header
                    if content_type is None:
                        headers = {'Content-Type': 'application/octet-stream'}
                    else:
                        headers = {'Content-Type': content_type}

                    if method == 'put':
                        response = self.interface.put(uri, data=file_handle, headers=headers, timeout=timeout)
                    elif method == 'post':
                        response = self.interface.post(uri, data=file_handle, headers=headers, timeout=timeout)
                    else:
                        raise ValueError('Invalid upload method "{}" should be either put or post.'.format(method))
                    self._check_response(response)
                    return response
                except exceptions.XNATResponseError:
                    pass
        finally:
            if opened_file:
                file_handle.close()

        # We didn't return correctly, so we have an error
        raise exceptions.XNATUploadError('Upload failed after {} attempts! Status code {}, response text {}'.format(retries, response.status_code, response.text))

    @property
    def scanners(self):
        """
        A list of scanners referenced in XNATSession
        """
        return [x['scanner'] for x in self.xnat_session.get_json('/data/archive/scanners')['ResultSet']['Result']]

    @property
    def scan_types(self):
        """
         A list of scan types associated with this XNATSession instance
        """
        return self.xnat_session.get_json('/data/archive/scan_types')['ResultSet']['Result']

    @property
    @caching
    def xnat_version(self):
        """
        The version of the XNAT server
        """
        try:
            # XNAT SERVER 1.6.x
            return self.get('/data/version').text
        except exceptions.XNATResponseError:
            # XNAT SERVER 1.7.x
            return self.get_json('/xapi/siteConfig/buildInfo')['version']

    def create_object(self, uri, type_=None, fieldname=None, **kwargs):
        if (uri, fieldname) not in self._cache['__objects__']:
            if type_ is None:
                if self.xnat_session.debug:
                    self.logger.debug('Type unknown, fetching data to get type')
                data = self.xnat_session.get_json(uri)
                type_ = data['items'][0]['meta']['xsi:type']
                datafields = data['items'][0]['data_fields']
            else:
                datafields = None

            if self.xnat_session.debug:
                self.logger.debug('Looking up type {} [{}]'.format(type_, type(type_).__name__))
            if type_ not in self.XNAT_CLASS_LOOKUP:
                raise KeyError('Type {} unknow to this XNATSession REST client (see XNAT_CLASS_LOOKUP class variable)'.format(type_))

            cls = self.XNAT_CLASS_LOOKUP[type_]

            if self.xnat_session.debug:
                self.logger.debug('Creating object of type {}'.format(cls))

            # Add project post-hoc hook for fixing some problems with shared
            # resources, the .+? is the non greedy version of .+
            match = re.search('/data(?:/archive)?/projects/(.+?)/', uri)

            if match:
                # Set overwrite field
                overwrites = {'project': match.group(1)}
            else:
                overwrites = None

            obj = cls(uri, self, datafields=datafields, fieldname=fieldname, overwrites=overwrites, **kwargs)

            self._cache['__objects__'][uri, fieldname] = obj
        elif self.debug:
            self.logger.debug('Fetching object {} from cache'.format(uri))

        return self._cache['__objects__'][uri, fieldname]

    @property
    @caching
    def projects(self):
        """
        Listing of all projects on the XNAT server

        Returns an :py:class:`XNATListing <xnat.core.XNATListing>` with elements
        of :py:class:`ProjectData <xnat.classes.ProjectData>`
        """
        return XNATListing(self.uri + '/projects',
                           xnat_session=self.xnat_session,
                           parent=self,
                           field_name='projects',
                           xsi_type='xnat:projectData',
                           secondary_lookup_field='name')

    @property
    @caching
    def subjects(self):
        """
        Listing of all subjects on the XNAT server

        Returns an :py:class:`XNATListing <xnat.core.XNATListing>` with elements
        of :py:class:`SubjectData <xnat.classes.SubjectData>`
        """
        return XNATListing(self.uri + '/subjects',
                           xnat_session=self.xnat_session,
                           parent=self,
                           field_name='subjects',
                           xsi_type='xnat:subjectData',
                           secondary_lookup_field='label')

    @property
    @caching
    def experiments(self):
        """
        Listing of all experiments on the XNAT server

        Returns an :py:class:`XNATListing <xnat.core.XNATListing>` with elements
        that are subclasses of :py:class:`ExperimentData <xnat.classes.ExperimentData>`
        """
        return XNATListing(self.uri + '/experiments',
                           xnat_session=self.xnat_session,
                           parent=self,
                           field_name='experiments',
                           secondary_lookup_field='label')

    @property
    def prearchive(self):
        """
        Representation of the prearchive on the XNAT server, see :py:mod:`xnat.prearchive`
        """
        return self._prearchive

    @property
    def users(self):
        """
        Representation of the users registered on the XNAT server
        """
        return self._users

    @property
    def services(self):
        """
        Collection of services, see :py:mod:`xnat.services`
        """
        return self._services

    def clearcache(self):
        """
        Clear the cache of the listings in the Session object
        """
        self._cache.clear()
        self._cache['__objects__'] = {}


def default_update_func(total):
    """
    Set up a default update function to be used by the
    :class:`Session.download_stream` method. This function configures a
    ``progressbar.ProgressBar`` object which displays progress as a file
    is downloaded.

    :param int total: Total number of bytes to be downloaded (might be
                      ``None``)

    :returns: A function to be used as the ``update_func`` by the
              ``Session.download_stream`` method.
    """

    if total is not None:
        widgets = [
            Percentage(),
            ' of ', DataSize('max_value'),
            ' ', Bar(),
            ' ', AdaptiveTransferSpeed(),
            ' ', AdaptiveETA(),
        ]
    else:
        total = UnknownLength
        widgets = [
            DataSize(),
            ' ', BouncingBar(),
            ' ', AdaptiveTransferSpeed(),
            ' ', Timer(),
        ]

    progress_bar = ProgressBar(widgets=widgets, max_value=total)

    # The real update function which gets called by download_stream
    def do_update(nbytes, total, finished, progress_bar=progress_bar):

        if nbytes == 0:
            progress_bar.start()
        elif finished:
            progress_bar.finish()
        else:
            progress_bar.update(nbytes)

    return do_update
