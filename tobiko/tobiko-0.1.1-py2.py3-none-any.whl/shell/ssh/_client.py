# Copyright (c) 2019 Red Hat, Inc.
#
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from __future__ import absolute_import

import os
import socket
import time

import paramiko
from oslo_log import log

import tobiko
from tobiko.shell.ssh import _config
from tobiko.shell.ssh import _command


LOG = log.getLogger(__name__)


SSH_CONNECT_PARAMETERS = {
    #: The server to connect to
    'hostname': str,

    #: The server port to connect to
    'port': int,

    #: The username to authenticate as (defaults to the current local username)
    'username': str,

    #: Used for password authentication; is also used for private key
    #: decryption if passphrase is not given
    'password': str,

    #: Used for decrypting private keys
    'passphrase': str,

    #: The filename, or list of filenames, of optional private key(s) and/or
    #: certs to try for authentication
    'key_filename': str,

    #: An optional timeout (in seconds) for the TCP connect
    'timeout': float,

    #: Set to False to disable connecting to the SSH agent
    'allow_agent': bool,

    #: Set to False to disable searching for discoverable private key files in
    #: ~/.ssh/
    'look_for_keys': bool,

    #: Set to True to turn on compression
    'compress': bool,

    #: True if you want to use GSS-API authentication
    'gss_auth': bool,

    #: Perform GSS-API Key Exchange and user authentication
    'gss_kex': bool,

    #: Delegate GSS-API client credentials or not
    'gss_deleg_creds': bool,

    #: The targets name in the kerberos database. default: hostname
    'gss_host': str,

    #: Indicates whether or not the DNS is trusted to securely canonicalize the
    #: name of the host being connected to (default True).
    'gss_trust_dns': bool,

    #: An optional timeout (in seconds) to wait for the SSH banner to be
    #: presented.
    'banner_timeout': float,

    #: An optional timeout (in seconds) to wait for an authentication response
    'auth_timeout': float,

    #: Number of connection attempts to be tried before timeout
    'connection_attempts': int,

    #: Minimum amount of time to wait between two connection attempts
    'connection_interval': float,

    #: Command to be executed to open proxy sock
    'proxy_command': str,
}


class SSHConnectFailure(tobiko.TobikoException):
    message = "Failed to login to {login}\n{cause}"


class SSHClientFixture(tobiko.SharedFixture):

    host = None
    client = None

    default = tobiko.required_setup_fixture(_config.SSHDefaultConfigFixture)
    config_files = None
    host_config = None

    proxy_client = None
    proxy_sock = None
    connect_parameters = None

    def __init__(self, host=None, proxy_client=None, host_config=None,
                 config_files=None, **connect_parameters):
        super(SSHClientFixture, self).__init__()
        if host:
            self.host = host
        if proxy_client:
            self.proxy_client = proxy_client
        if host_config:
            self.host_config = host_config
        if config_files:
            self.config_files = config_files
        invalid_parameters = sorted([name
                                     for name in connect_parameters
                                     if name not in SSH_CONNECT_PARAMETERS])
        if invalid_parameters:
            message = "Invalid SSH connection parameters: {!s}".format(
                ', '.join(invalid_parameters))
            raise ValueError(message)
        self._connect_parameters = connect_parameters

    def setup_fixture(self):
        self.setup_host_config()
        self.setup_connect_parameters()
        self.setup_ssh_client()

    def setup_host_config(self):
        if not self.host_config:
            self.host_config = _config.ssh_host_config(
                host=self.host, config_files=self.config_files)

    def setup_connect_parameters(self):
        """Fill connect parameters dict

        Get parameters values from below sources:
        - parameters passed to class constructor
        - parameters got from ~/.ssh/config and tobiko.conf
        - parameters got from fixture object attributes
        """

        # Get default parameter values from self object
        self.connect_parameters = parameters = items_from_object(
            schema=SSH_CONNECT_PARAMETERS, obj=self)
        LOG.debug('Default parameters for host %r:\n%r', self.host,
                  parameters)

        # Override parameters from host configuration files
        parameters.update(
            items_from_mapping(schema=SSH_CONNECT_PARAMETERS,
                               mapping=self.host_config.connect_parameters))
        LOG.debug('Configured connect parameters for host %r:\n%r',
                  self.host, parameters)

        # Override parameters with __init__ parameters
        parameters.update(
            items_from_mapping(schema=SSH_CONNECT_PARAMETERS,
                               mapping=self._connect_parameters))
        LOG.debug('Resulting connect parameters for host %r:\n%r', self.host,
                  parameters)

        # Validate hostname
        hostname = parameters.get('hostname')
        if not hostname:
            message = "Invalid hostname: {!r}".format(hostname)
            raise ValueError(message)

        # Expand key_filename
        key_filename = parameters.get('key_filename')
        if key_filename:
            key_filename = os.path.expanduser(key_filename)
            if not os.path.exists(key_filename):
                message = "key_filename {!r} doesn't exist".format(hostname)
                raise ValueError(message)
            parameters['key_filename'] = key_filename

        # Validate connection timeout
        timeout = parameters.get('timeout')
        if not timeout or timeout < 0.:
            message = "Invalid timeout: {!r}".format(timeout)
            raise ValueError(message)

        # Validate connection attempts
        connection_attempts = parameters.get('connection_attempts')
        if not connection_attempts or connection_attempts < 0:
            message = "Invalid connection attempts: {!r}".format(
                connection_attempts)
            raise ValueError(message)

        # Validate connection attempts
        connection_interval = parameters.get('connection_interval')
        if not connection_interval or connection_interval < 0.:
            message = "Invalid connection interval: {!r}".format(
                connection_interval)
            raise ValueError(message)

        # Validate connection port
        port = parameters.get('port')
        if not port or port < 1 or port > 65535:
            message = "Invalid port: {!r}".format(port)
            raise ValueError(message)

    def setup_ssh_client(self):
        self.client, self.proxy_sock = ssh_connect(
            proxy_client=self.proxy_client, **self.connect_parameters)
        self.addCleanup(self.client.close)
        if self.proxy_sock:
            self.addCleanup(self.proxy_sock.close)

    def connect(self):
        return tobiko.setup_fixture(self).client


def items_from_mapping(schema, mapping):
    return ((key, init(mapping.get(key)))
            for key, init in schema.items()
            if mapping.get(key) is not None)


def items_from_object(schema, obj):
    return {key: init(getattr(obj, key, None))
            for key, init in schema.items()
            if getattr(obj, key, None) is not None}


UNDEFINED_CLIENT = 'UNDEFINED_CLIENT'


class SSHClientManager(object):

    default = tobiko.required_setup_fixture(_config.SSHDefaultConfigFixture)

    def __init__(self):
        self.clients = {}

    def get_client(self, host, username=None, port=None, proxy_jump=None,
                   host_config=None, config_files=None, **connect_parameters):
        host_config = host_config or _config.ssh_host_config(
            host=host, config_files=config_files)
        hostname = host_config.hostname
        port = port or host_config.port
        username = username or host_config.username
        host_key = hostname, port, username, proxy_jump
        client = self.clients.get(host_key, UNDEFINED_CLIENT)
        if client is UNDEFINED_CLIENT:
            # Put a placeholder client to avoid infinite recursive lookup
            self.clients[host_key] = None
            proxy_client = self.get_proxy_client(host=host,
                                                 config_files=config_files)
            self.clients[host_key] = client = SSHClientFixture(
                host=host, hostname=hostname, port=port, username=username,
                proxy_client=proxy_client, **connect_parameters)
        return client

    def get_proxy_client(self, host=None, host_config=None,
                         config_files=None):
        host_config = host_config or _config.ssh_host_config(
            host=host, config_files=config_files)
        proxy_host = host_config.proxy_jump
        return proxy_host and self.get_client(proxy_host) or None


CLIENTS = SSHClientManager()


def ssh_client(host, port=None, username=None, proxy_jump=None,
               host_config=None, config_files=None, manager=None,
               **connect_parameters):
    manager = manager or CLIENTS
    return manager.get_client(host=host, port=port, username=username,
                              proxy_jump=proxy_jump, host_config=host_config,
                              config_files=config_files,
                              **connect_parameters)


def ssh_connect(hostname, username=None, port=None, connection_interval=None,
                connection_attempts=None, proxy_command=None,
                proxy_client=None, **parameters):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.load_system_host_keys()

    login = _command.ssh_login(hostname=hostname, username=username, port=port)
    attempts = connection_attempts or 1
    interval = connection_interval or 5.
    for attempt in range(1, attempts + 1):
        LOG.debug("Logging in to %r (%r)... attempt %d out of %d",
                  login, parameters, attempt, attempts)
        start_time = time.time()
        proxy_sock = ssh_proxy_sock(hostname=hostname,
                                    port=port,
                                    command=proxy_command,
                                    client=proxy_client)
        try:
            client.connect(hostname=hostname,
                           username=username,
                           port=port,
                           sock=proxy_sock,
                           **parameters)
        except (EOFError, socket.error, socket.timeout,
                paramiko.SSHException) as ex:
            if attempt >= attempts:
                raise

            LOG.debug("Error logging in to %r: \n(%s)", login, ex)
            sleep_time = start_time + interval - time.time()
            if sleep_time > 0.:
                LOG.debug("Retrying connecting to %r in %d seconds...", login,
                          sleep_time)
                time.sleep(sleep_time)

        else:
            LOG.info("Successfully logged it to %s", login)
            return client, proxy_sock


def ssh_proxy_sock(hostname, port=None, command=None, client=None):
    if client:
        # I need a command to execute with proxy client
        command = command or 'nc {hostname!r} {port!r}'
    elif not command:
        # Proxy sock is not required
        return None

    # Apply connect parameters to proxy command
    command = command.format(hostname=hostname, port=(port or 22))
    if client:
        if isinstance(client, SSHClientFixture):
            # Connect to proxy server
            client = client.connect()
        elif not isinstance(client, paramiko.SSHClient):
            message = "Object {!r} is not an SSHClient".format(client)
            raise TypeError(message)

        # Open proxy channel
        LOG.debug("Execute proxy command with proxy client %r: %r",
                  client, command)
        sock = client.get_transport().open_session()
        sock.exec_command(command)
    else:
        LOG.debug("Execute proxy command on local host: %r", command)
        sock = paramiko.ProxyCommand(command)

    return sock


def ssh_proxy_client(manager=None, host=None, host_config=None,
                     config_files=None):
    manager = manager or CLIENTS
    return manager.get_proxy_client(host=host,
                                    host_config=host_config,
                                    config_files=config_files)
