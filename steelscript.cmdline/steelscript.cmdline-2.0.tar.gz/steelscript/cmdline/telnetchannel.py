# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import logging
import telnetlib
import socket

from steelscript.cmdline import exceptions
from steelscript.cmdline import channel


class SteelScriptTelnet(telnetlib.Telnet):
    """Local subclass to facilitate logging."""
    def msg(self, msg, *args):
        """ Forward telnetlib's debug messages to log """
        context = 'Telnet(%s,%d):' % (self.host, self.port)
        logging.debug(context + msg, *args)


class TelnetChannel(channel.Channel):
    """
    Two-way telnet channel that allows sending and receiving data.

    Accepts and ignores additional parameters for compatibility
    with other channel construction interfaces.

    :param hostname: host/ip to telnet into
    :param username: username to log in with
    :param password: password to log in with
    :param port: telnet port, defaults to 23
    """

    LOGIN_PROMPT = r'(^|\n|\r)(L|l)ogin: '
    PASSWORD_PROMPT = r'(^|\n|\r)(P|p)assword: '
    ENTER_LINE = r'\r'

    BASH_PROMPT = r'\[\S+ \S+\]#\s*$'

    def __init__(self, hostname, username='root', password='', port=23,
                 **kwargs):

        # Hostname to connects
        self._host = hostname

        self._user = username
        self._password = password
        self._port = port

        # SteelScriptTelnet
        self.channel = None

    def start(self, match_res=None, timeout=15):
        """
        Start telnet session and log it in

        :param match_res: Pattern(s) of prompts to look for.
                          May be a single regex string, or a list of them.
        :param timeout: maximum time, in seconds, to wait for a regular
                        expression match. 0 to wait forever.
        :return: Python re.MatchObject containing data on what was matched.
        """

        if not match_res:
            match_res = [self.BASH_PROMPT]
        elif not isinstance(match_res, list) or isinstance(match_res, tuple):
            match_res = [match_res, ]

        # Start channel
        self.channel = SteelScriptTelnet(self._host, self._port)

        return self._handle_init_login(match_res, timeout)

    def close(self):
        if self.channel is not None:
            self.channel.close()

    def _handle_init_login(self, match_res, timeout):
        """
        Handle initial login.

        :param match_res: Pattern(s) of prompts to look for after login.
            May be a single regex string, or a list of them.
        :param timeout: maximum time, in seconds, to wait for a regular
            expression match. 0 to wait forever.
        :return: Python :class:`re.MatchObject` containing data on what
            was matched after login.
        :raises CmdlineTimeout: if any step of the login exceeds the timeout.
        """

        # Add login prompt and password prompt so that we can detect
        # what require for login
        reg_with_login_prompts = match_res
        reg_with_login_prompts.insert(0, self.PASSWORD_PROMPT)
        reg_with_login_prompts.insert(0, self.LOGIN_PROMPT)

        (index, match, data) = self.channel.expect(reg_with_login_prompts,
                                                   timeout)

        if index == 0:
            # username is required for login
            logging.debug("Sending login user ...")
            # We are Python3 now - everything is unicode, right?
            text_to_send = (self._user + self.ENTER_LINE)
            self.channel.write(text_to_send)
            (index, match, data) = self.channel.expect(reg_with_login_prompts,
                                                       timeout)
        if index == 1:
            # password is required for login
            logging.debug("Sending password ...")
            # We are Python3 now - everything is unicode, right?
            text_to_send = (self._password + self.ENTER_LINE)
            self.channel.write(text_to_send)
            (index, match, data) = self.channel.expect(reg_with_login_prompts,
                                                       timeout)
        # At this point, we should already logged in; raises exceptions if not
        if index < 0:
            raise exceptions.CmdlineTimeout(timeout=timeout,
                                            failed_match=match_res)
        elif index in (0, 1):
            logging.info("Login failed, still waiting for %s prompt",
                         ('username' if index == 0 else 'password'))
            raise exceptions.CmdlineTimeout(
                timeout=timeout,
                failed_match=reg_with_login_prompts[index])

        # Login successfully if reach this point
        logging.info('Telnet channel to "%s" started' % self._host)
        return match

    def _verify_connected(self):
        """
        Verifies an established connection and transport.

        :raises ConnectionError: if we are not connected
        """

        if not self.channel:
            raise exceptions.ConnectionError(
                context='Channel has not been started')

        # Send an NOP to see whether connection is still alive.
        try:
            self.channel.sock.sendall(telnetlib.IAC + telnetlib.NOP)
        except socket.error:
            logging.exception('Host SSH shell has been disconnected')
            raise exceptions.ConnectionError

    def receive_all(self):
        """
        Flushes the receive buffer, returning all text that was in it.

        :return: the text that was present in the receive queue, if any.
        """

        logging.debug('Receiving all data')
        return self.channel.read_very_eager()

    def send(self, text_to_send):
        """
        Sends text to the channel immediately.  Does not wait for any response.

        :param text_to_send: Text to send, may be an empty string.
        """
        logging.debug('Sending "%s"' % self.safe_line_feeds(text_to_send))
        self.channel.write(text_to_send)

    def expect(self, match_res, timeout=60):
        """
        Waits for some text to be received that matches one or more regex
        patterns.

        Note that data may have been received before this call and is waiting
        in the buffer; you may want to call receive_all() to flush the receive
        buffer before calling send() and call this function to match the
        output from your send() only.

        :param match_res: Pattern(s) to look for to be considered successful.
                          May be a single regex string, or a list of them.
        :param timeout: maximum time, in seconds, to wait for a regular
                        expression match. 0 to wait forever.

        :return: ``(output, match_object)`` where output is the output of
            the command (without the matched text), and match_object is a
            Python :class:`re.MatchObject` containing data on what was matched.

            You may use ``MatchObject.string[m.start():m.end()]`` to recover
            the actual matched text, which will be unicode.

            ``re.MatchObject.pattern`` will contain the pattern that matched,
            which will be one of the elements of match_res passed in.

        :raises CmdlineTimeout: if no match found before timeout.
        """

        match_res, safe_match_text = self._expect_init(match_res)
        (index, matched, data) = self.channel.expect(match_res, timeout)
        if index == -1:
            raise exceptions.CmdlineTimeout(timeout=timeout,
                                            failed_match=match_res)
        # Remove matched string at the end
        length = matched.start() - matched.end()
        if length < 0:
            data = data[:length]

        # Normalize carriage returns
        data = self.fixup_carriage_returns(data)

        return (data, matched)
