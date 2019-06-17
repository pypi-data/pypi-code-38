# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.
#
# Basic SSH shell, wrapped around Paramiko
# Modified based on codes from mgmt-fwk


import paramiko
import logging

from steelscript.cmdline import exceptions
from steelscript.cmdline import transport


class SSHProcess(transport.Transport):
    """
    SSH transport class to handle ssh connection setup.

    :param host: host/ip to ssh into
    :param user: username to log in with
    :param password: password to log in with
    :param private_key: paramiko private key (Pkey) object

    If a private_key is passed, it will take precendence over a password,
    no fallback attempt will be made if the private key connection fails,
    however.
    """

    # Seconds to wait for banner coming out after starting connection.
    BANNER_TIMEOUT = 5

    def __init__(self, host, user='root', password=None, private_key=None,
                 port=22):
        # Hostname shell connects to
        self._host = host
        self._port = port

        # Username shell connects with
        self._user = user

        # Password shell connects with
        self._password = password

        # Private key as paramiko.pkey.PKey
        self._private_key = private_key

        # paramiko.Transport object, the actual SSH engine.
        # http://www.lag.net/paramiko/docs/
        self.transport = None

        # Logging module
        self._log = logging.getLogger(__name__)

    def connect(self):
        """
        Connects to the host and logs in.

        :raises ConnectionError: on error
        """
        self._log.info('Connecting to "%s" as "%s"' % (self._host, self._user))
        try:
            self.transport = paramiko.Transport((self._host, self._port))
            self.transport.banner_timeout = self.BANNER_TIMEOUT
            self.transport.start_client()

            if self._private_key:
                self.transport.auth_publickey(self._user, self._private_key)
            else:
                self.transport.auth_password(self._user, self._password,
                                             fallback=True)
        except paramiko.ssh_exception.SSHException:
            # Close the session, or the child thread apparently hangs
            self.disconnect()
            self._log.exception("Could not connect to %s", self._host)
            raise exceptions.ConnectionError

    def disconnect(self):
        """
        Disconnects from the host
        """

        if self.transport:
            self.transport.close()

    def is_connected(self):
        """
        Check whether SSH connection is established or not.

        :return: True if it is connected; returns False otherwise.
        """
        if self.transport and self.transport.is_active():
            return True
        return False

    def open_interactive_channel(self, term='console', width=80, height=24):
        """
        Creates and starts a stateful interactive channel.

        This should be used whenever the channel must remain open between
        commands for interactive processing, or when a terminal/tty is
        necessary; e.g., CLIs with modes.

        :param term: terminal type to emulate; defaults to 'console'
        :param width: width (in characters) of the terminal screen;
            defaults to 80
        :param height: height (in characters) of the terminal screen;
            defaults to 24

        :return: A Paramiko channel that communicate with the remote end in
            a stateful way.

        :raises ConnectionError: if the SSH connection has not yet been
            established.
        """

        if (not self.is_connected()):
            raise exceptions.ConnectionError(context='Not connected!')

        channel = self.transport.open_session()
        channel.get_pty(term, width, height)
        channel.invoke_shell()
        channel.set_combine_stderr(True)
        return channel
