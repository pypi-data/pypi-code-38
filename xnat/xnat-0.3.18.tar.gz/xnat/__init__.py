# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
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

"""
This package contains the entire client. The connect function is the only
function actually in the package. All following classes are created based on
the https://central.xnat.org/schema/xnat/xnat.xsd schema and the xnatcore and
xnatbase modules, using the convert_xsd.
"""

from __future__ import absolute_import
from __future__ import unicode_literals
import getpass
import hashlib
import imp
import logging
import os
import netrc
import re
import tempfile
import time

import requests
from six.moves.urllib import parse

from . import exceptions
from .session import XNATSession
from .constants import DEFAULT_SCHEMAS
from .convert_xsd import SchemaParser

GEN_MODULES = {}

__version__ = '0.3.18'
__all__ = ['connect', 'exceptions']


def check_auth(requests_session, server, user, logger):
    """
    Try to figure out of the requests session is properly logged in as the desired user

    :param requests.Session requests_session: requests session
    :param str server: server test
    :param str user: desired user (None for guest)
    :raises ValueError: Raises a ValueError if the login failed
    """
    logger.debug('Getting {} to test auth'.format(server))
    test_auth_request = requests_session.get(server)
    logger.debug('Status: {}'.format(test_auth_request.status_code))

    if test_auth_request.status_code == 401 or 'Login attempt failed. Please try again.' in test_auth_request.text:
        message = 'Login attempt failed for {}, please make sure your credentials for user {} are correct!'.format(server, user)
        logger.critical(message)
        raise exceptions.XNATLoginFailedError(message)

    if test_auth_request.status_code != 200:
        logger.warning('Simple test requests did not return a 200 code! Server might not be functional!')

    if user is not None:
        match = re.search(r'<span id="user_info">Logged in as: &nbsp;<a (id="[^"]+" )?href="[^"]+">(?P<username>[^<]+)</a>',
                          test_auth_request.text)

        if match is None:
            match = re.search(r'<span id="user_info">Logged in as: <span style="color:red;">Guest</span>',
                              test_auth_request.text)
            if match is None:
                match = re.search('Your password has expired', test_auth_request.text)
                if match:
                    message = 'Your password has expired. Please try again after updating your password on XNAT.'
                    logger.error(message)
                    raise exceptions.XNATExpiredCredentialsError(message)
                else:
                    message = 'Could not determine if login was successful!'
                    logger.error(message)
                    logger.debug(test_auth_request.text)
                    raise exceptions.XNATAuthError(message)
            else:
                message = 'Login failed (in guest mode)!'
                logger.error(message)
                raise exceptions.XNATLoginFailedError(message)
        else:
            username = match.group('username')
            logger.info('Logged in successfully as {}'.format(username))
            return username

    match = re.search(r'<span id="user_info">Logged in as: <span style="color:red;">Guest</span>',
                      test_auth_request.text)
    if match is None:
        message = 'Could not determine if login was successful!'
        logger.error(message)
        raise exceptions.XNATAuthError(message)
    else:
        logger.info('Logged in as guest successfully')
        return 'guest'


def parse_schemas_16(parser, xnat_session, extension_types=True):
    """
    Retrieve and parse schemas for an XNAT version 1.6.x

    :param parser: The parser to use for the parsing
    :param requests_session: the requests session used for the communication
    :param str server: URI of the XNAT server
    :param logger: logger to use for the logging
    :param bool extension_types: flag to enabled/disable scanning for extension types
    """
    # Retrieve schema from XNAT server
    schema_uri = '/schemas/xnat/xnat.xsd'

    success = parser.parse_schema_uri(xnat_session=xnat_session,
                                      schema_uri=schema_uri)

    if not success:
        raise RuntimeError('Could not parse the xnat.xsd! See error log for details!')

    # Parse extension types
    if extension_types:
        projects_uri = '/data/projects?format=json'
        try:
            response = xnat_session.get(projects_uri)
        except exceptions.XNATResponseError as exception:
            message = 'Could list projects while scanning for extension types: {}'.format(exception)
            xnat_session.logger.critical(message)
            raise exception

        try:
            project_id = response.json()['ResultSet']['Result'][0]['ID']
        except (KeyError, IndexError):
            raise ValueError('Could not find an example project for scanning extension types!')

        project_uri = '/data/projects/{}'.format(project_id)
        try:
            response = xnat_session.get(project_uri, format='xml')
        except exceptions.XNATResponseError as exception:
            message = 'Could load example project while scanning for extension types: {}'.format(exception)
            xnat_session.logger.critical(message)
            raise exception

        schemas = parser.find_schema_uris(response.text)
        if schema_uri in schemas:
            xnat_session.logger.debug('Removing schema {} from list'.format(schema_uri))
            schemas.remove(schema_uri)
        xnat_session.logger.info('Found additional schemas: {}'.format(schemas))

        for schema in schemas:
            parser.parse_schema_uri(xnat_session=xnat_session,
                                    schema_uri=schema)


def parse_schemas_17(parser, xnat_serssion, extension_types=True):
    """
    Retrieve and parse schemas for an XNAT version 1.7.x

    :param parser: The parser to use for the parsing
    :param requests_session: the requests session used for the communication
    :param str server: URI of the XNAT server
    :param logger: logger to use for the logging
    """
    if extension_types:
        schemas_uri = '/xapi/schemas'
        try:
            schema_list = xnat_serssion.get_json(schemas_uri)
        except exceptions.XNATResponseError as exception:
            message = 'Problem retrieving schemas list: {}'.format(exception)
            xnat_serssion.logger.critical(message)
            raise ValueError(message)
    else:
        schema_list = DEFAULT_SCHEMAS

    for schema in schema_list:
        if extension_types or schema in ['xdat', 'xnat']:
            parser.parse_schema_uri(xnat_session=xnat_serssion,
                                    schema_uri='/xapi/schemas/{schema}'.format(schema=schema))


def detect_redirection(server, session, logger):
    """
    Check if there is a redirect going on
    :param str server: server url
    :param session: requests session to use for the connection
    :param logger:
    :return: the server url to use later
    """
    response = session.get(server.rstrip('/') + '/data/projects')
    logger.debug('Response url: {}'.format(response.url))
    response_url = response.url[:-13]
    if response_url != server and response_url != server + '/':
        logger.warning('Detected a redirect from {0} to {1}, using {1} from now on'.format(server, response_url))
    return response_url


def query_netrc(server, netrc_file, logger):
    # Get the login info
    parsed_server = parse.urlparse(server)

    logger.info('Retrieving login info for {}'.format(parsed_server.netloc))
    try:
        if netrc_file is None:
            netrc_file = os.path.join('~', '_netrc' if os.name == 'nt' else '.netrc')
            netrc_file = os.path.expanduser(netrc_file)
        user, _, password = netrc.netrc(netrc_file).authenticators(parsed_server.netloc)
        logger.info('Found login for {}'.format(parsed_server.netloc))
    except (TypeError, IOError):
        logger.info('Could not find login for {}, continuing without login'.format(parsed_server.netloc))
        user = password = None

    return user, password


def build_model(xnat_session, extension_types, connection_id):
    """
    Build the XNAT data model for a given connection
    """
    logger = xnat_session.logger
    debug = xnat_session.debug

    # Check XNAT version
    version = xnat_session.xnat_version

    # Generate module
    parser = SchemaParser(debug=debug, logger=logger)

    if xnat_session.xnat_version.startswith('1.6'):
        logger.info('Found an 1.6 version ({})'.format(version))
        parse_schemas_16(parser, xnat_session, extension_types=extension_types)
    elif version.startswith('1.7'):
        logger.info('Found an 1.7 version ({})'.format(version))
        parse_schemas_17(parser, xnat_session, extension_types=extension_types)
    else:
        logger.critical('Found an unsupported version ({})'.format(version))
        raise ValueError('Cannot continue on unsupported XNAT version')

    # Write code to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='_generated_xnat.py', delete=False) as code_file:
        parser.write(code_file=code_file)

    logger.debug('Code file written to: {}'.format(code_file.name))

    # The module is loaded in its private namespace based on the code_file name
    xnat_module = imp.load_source('xnat_gen_{}'.format(connection_id),
                                  code_file.name)
    xnat_module._SOURCE_CODE_FILE = code_file.name

    logger.debug('Loaded generated module')

    # Register all types parsed
    for cls in parser.class_list.values():
        if not (cls.name is None or (cls.base_class is not None and cls.base_class.startswith('xs:'))):
            getattr(xnat_module, cls.writer.python_name).__register__(xnat_module.XNAT_CLASS_LOOKUP)

    xnat_module.SESSION = xnat_session

    # Add the required information from the module into the xnat_session object
    xnat_session.XNAT_CLASS_LOOKUP.update(xnat_module.XNAT_CLASS_LOOKUP)
    xnat_session.classes = xnat_module
    xnat_session._source_code_file = code_file.name


def connect(server, user=None, password=None, verify=True, netrc_file=None, debug=False,
            extension_types=True, loglevel=None, logger=None, detect_redirect=True,
            no_parse_model=False):
    """
    Connect to a server and generate the correct classed based on the servers xnat.xsd
    This function returns an object that can be used as a context operator. It will call
    disconnect automatically when the context is left. If it is used as a function, then
    the user should call ``.disconnect()`` to destroy the session and temporary code file.

    :param str server: uri of the server to connect to (including http:// or https://)
    :param str user: username to use, leave empty to use netrc entry or anonymous login.
    :param str password: password to use with the username, leave empty when using netrc.
                         If a username is given and no password, there will be a prompt
                         on the console requesting the password.
    :param bool verify: verify the https certificates, if this is false the connection will
                        be encrypted with ssl, but the certificates are not checked. This is
                        potentially dangerous, but required for self-signed certificates.
    :param str netrc_file: alternative location to use for the netrc file (path pointing to
                           a file following the netrc syntax)
    :param debug bool: Set debug information printing on and print extra debug information.
                       This is meant for xnatpy developers and not for normal users. If you
                       want to debug your code using xnatpy, just set the loglevel to DEBUG
                       which will show you all requests being made, but spare you the
                       xnatpy internals.
    :param str loglevel: Set the level of the logger to desired level
    :param logging.Logger logger: A logger to reuse instead of creating an own logger
    :param bool detect_redirect: Try to detect a redirect (via a 302 response) and short-cut
                                 for subsequent requests
    :param bool no_parse_model: Create an XNAT connection without parsing the server data
                                model, this create a connection for which the simple
                                get/head/put/post/delete functions where, but anything
                                requiring the data model will file (e.g. any wrapped classes)
    :return: XNAT session object
    :rtype: XNATSession

    Preferred use::

        >>> import xnat
        >>> with xnat.connect('https://central.xnat.org') as session:
        ...    subjects = session.projects['Sample_DICOM'].subjects
        ...    print('Subjects in the SampleDICOM project: {}'.format(subjects))
        Subjects in the SampleDICOM project: <XNATListing (CENTRAL_S01894, dcmtest1): <SubjectData CENTRAL_S01894>, (CENTRAL_S00461, PACE_HF_SUPINE): <SubjectData CENTRAL_S00461>>

    Alternative use::

        >>> import xnat
        >>> session = xnat.connect('https://central.xnat.org')
        >>> subjects = session.projects['Sample_DICOM'].subjects
        >>> print('Subjects in the SampleDICOM project: {}'.format(subjects))
        Subjects in the SampleDICOM project: <XNATListing (CENTRAL_S01894, dcmtest1): <SubjectData CENTRAL_S01894>, (CENTRAL_S00461, PACE_HF_SUPINE): <SubjectData CENTRAL_S00461>>
        >>> session.disconnect()
    """

    # Generate a hash for the connection
    hasher = hashlib.md5()
    hasher.update(server.encode('utf-8'))
    hasher.update(str(time.time()).encode('utf-8'))
    connection_id = hasher.hexdigest()

    # Setup the logger for this connection
    if logger is None:
        logger = logging.getLogger('xnat-{}'.format(connection_id))
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)

        # create formatter
        if debug:
            formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(module)s:%(lineno)d >> %(message)s')
        else:
            formatter = logging.Formatter('[%(levelname)s] %(message)s')
        handler.setFormatter(formatter)

        if loglevel is not None:
            logger.setLevel(loglevel)
        elif debug:
            logger.setLevel('DEBUG')
        else:
            logger.setLevel('WARNING')

    # If verify is False, disable urllib3 warning and give a one time warning!
    if not verify:
        logger.warning('Verify is disabled, this will NOT verify the certificate of SSL connections!')
        logger.warning('Warnings about invalid certificates will be HIDDEN to avoid spam, but this')
        logger.warning('means that your connection can be potentially unsafe!')
        requests.packages.urllib3.disable_warnings()

    if user is None and password is None:
        user, password = query_netrc(server, netrc_file, logger)

    if user is not None and password is None:
        password = getpass.getpass(prompt=str("Please enter the password for user '{}':".format(user)))

    # Create the correct requests session
    requests_session = requests.Session()

    if user is not None:
        requests_session.auth = (user, password)

    if not verify:
        requests_session.verify = False

    # Check for redirects
    original_uri = server
    if detect_redirect:
        server = detect_redirection(server, requests_session, logger)

    # If no login was found, check if the new server has a known login as a backup
    if original_uri != server and user is None and password is None:
        user, password = query_netrc(server, netrc_file, logger)

    # Check if login is successful
    logged_in_user = check_auth(requests_session, server=server, user=user, logger=logger)

    # Create the XNAT connection
    xnat_session = XNATSession(server=server, logger=logger,
                               interface=requests_session, debug=debug,
                               original_uri=original_uri, logged_in_user=logged_in_user)

    # Parse data model and create classes
    if not no_parse_model:
        build_model(xnat_session, extension_types=extension_types, connection_id=connection_id)

    return xnat_session
