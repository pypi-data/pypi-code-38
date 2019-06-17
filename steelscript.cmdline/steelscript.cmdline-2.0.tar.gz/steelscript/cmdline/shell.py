# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


import paramiko
import logging
import time
import select
import socket
import traceback

from steelscript.cmdline import sshprocess
from steelscript.cmdline import exceptions


class Shell(object):
    """
    Class for running shell command remotely and statelessly.

    No persistent channel is maintained, so changes to
    environment variables or other state will not be present for
    subsequent commands.

    :param host: host/ip to ssh into
    :param user: username to log in with
    :param password: password to log in with
    """

    def __init__(self, host, user='root', password=''):
        # Hostname shell connects to
        self._host = host

        # Username shell connects with
        self._user = user

        # Password shell connects with
        self._password = password

        # Initialize underlying sshprocess, but do not connect automatically.
        # http://www.lag.net/paramiko/docs/
        self.sshprocess = sshprocess.SSHProcess(host=host, user=user,
                                                password=password)

    def exec_command(self, command, timeout=60, output_expected=None,
                     error_expected=False, exit_info=None, retry_count=3,
                     retry_delay=5,
                     # Deprecated parameters. Remove for SteelScript.
                     expect_output=None, expect_error=None):
        """Executes the given command statelessly.

        Since this is stateless, an exec_command cannot use environment
        variables/directory changes/whatever from a previous exec_command.

        This method handles detecting simple boolean conditions such as
        the presence of output or errors.

        :param command: command to send
        :param timeout: seconds to wait for command to finish. None to disable
        :param output_expected: If not None, indicates whether output is
            expected (True) or no output is expected (False).
            If the opposite occurs, raise UnexpectedOutput. Default is None.
        :type output_expected: bool or None
        :param error_expected: If true, a nonzero exit status will **not**
            trigger an exception as it normally would.
            Default is False, and error_expected always
            overrides output_expected.
        :type error_expected: bool
        :param exit_info: If set to a dict, the exit status is added to
            the dictionary under the key 'status'.  Primarily used in
            conjunction with ``error_expected`` when multiple nonzero statuses
            are possible.
        :type exit_info: dict or None
        :param retry_count: the number of tries to reconnect if underlying
            connection is disconnected. Default is 3
        :type retry_count: int
        :param retry_delay: delay in seconds between each retry to connect.
            Default is 5
        :type retry_delay: int

        :return: output from the command

        :raises ConnectionError: if the connection is lost
        :raises CmdlineTimeout: on timeout
        :raises ShellError: on an unexpected nonzero exit status
        :raises UnexpectedOutput: if output occurs when no output was
            expected, or no output occurs when output was expected
        """

        logging.debug('Executing command "%s"' % command)

        # connect if ssh is not connected
        if (not self.sshprocess.is_connected()):
            self.sshprocess.connect()

        output, exit_status = self._exec_paramiko_command(
            command,
            timeout=timeout,
            retry_count=retry_count,
            retry_delay=retry_delay)

        if isinstance(exit_info, dict):
            exit_info['status'] = exit_status

        # If the command failed and the user wants an exception, do it!
        if exit_status != 0 and not error_expected:
            raise exceptions.ShellError(command=command,
                                        output=output,
                                        exit_status=exit_status)
        if ((output_expected is not None) and (bool(output) !=
                                               bool(output_expected))):
            raise exceptions.UnexpectedOutput(command=command,
                                              output=output,
                                              expected_output=output_expected)
        return output

    def _exec_paramiko_command(self, command, timeout, retry_count,
                               retry_delay):
        try:
            channel = self.sshprocess.transport.open_session()
        except socket.error:
            if retry_count == 0:
                logging.error("Socket Error %s" % traceback.format_exc())
                raise exceptions.ConnectionError

            # Reconnect and try again
            logging.info("connection seems broken, reconnect...")
            self._reconnect(retry_count=retry_count, retry_delay=retry_delay)
            channel = self.sshprocess.transport.open_session()

        # Put stderr into the same output as stdout.
        channel.set_combine_stderr(True)

        starttime = time.time()

        # Paramiko 1.7.5 has a bug in its internal event system
        # that can cause it to sometimes throw a 'not connected' exception when
        # running exec_command.  If we get that exception here, but we're still
        # connected, then just eat the exception and go on, since that's the
        # normal case.  This will hopefully be fixed in 1.7.6 and this
        # try/except removed.
        try:
            channel.exec_command(command)
        except paramiko.SSHException:
            if not self.sshprocess.is_connected():
                logging.info("Not connected to %s", self._host)
                logging.error("SSHException %s" % traceback.format_exc())
                raise exceptions.ConnectionError
            else:
                logging.debug(
                    'Ignore Paramiko SSHException due to 1.7.5 bug')

        chan_closed = False
        output = ""

        # Read until we time out or the channel closes
        while not chan_closed:

            # Use select to check whether channel is ready for read.
            # Reading on the channel directly would block until data is
            # ready, where select blocks at most 10 seconds which allows
            # us to check whether the specified timeout has been reached.
            # If channel is not ready for reading within 10 seconds,
            # select returns an empty list to 'readers'.
            (readers, w, x) = select.select([channel], [], [], 10)

            # Timeout if this is taking too long.
            if timeout and ((time.time() - starttime) > timeout):
                raise exceptions.CmdlineTimeout(command=command,
                                                timeout=timeout)

            # If the reader-ready list isn't empty, then read.  We know it must
            # be channel here, since thats all we're waiting on.
            if len(readers) > 0:
                data = channel.recv(4096)

                # If we get no data back, the channel has closed.
                if len(data) > 0:
                    output += data
                else:
                    chan_closed = True

            elif channel.exit_status_ready():
                # If no readers were available, see if the
                # exit status is ready - if so, the channel must be closed.
                # exit_status_ready can return true before we've read all the
                # data.  Problem is, I know I've seen it return true when there
                # was no data, and then data came in afterwards, so this might
                # occasionally trip early.  If only paramiko.channel had a way
                # to see if it was closed..
                chan_closed = True

        # Done reading.  Now we need to wait for the exit status/channel close.
        # Rather than block here, we'll poll to ensure we don't get stuck.
        while not channel.exit_status_ready():
            if timeout and ((time.time() - starttime) > timeout):
                raise exceptions.CmdlineTimeout(command=command,
                                                timeout=timeout)
            else:
                time.sleep(0.5)

        exit_status = channel.recv_exit_status()
        channel.close()

        return output, exit_status

    def _reconnect(self, retry_count, retry_delay):
        if not isinstance(retry_count, int) or retry_count < 1:
            raise TypeError("retry_count should be positive int")
        if not isinstance(retry_delay, int) or retry_delay < 1:
            raise TypeError("retry_delay should be positive int")

        for count in range(retry_count):
            try:
                self.sshprocess.connect()
                return
            except exceptions.ConnectionError:
                logging.info("sleep %d second and retry..." % retry_delay)
                time.sleep(retry_delay)

        raise exceptions.ConnectionError("Failed to connect after "
                                         "%d retries" % retry_count)
