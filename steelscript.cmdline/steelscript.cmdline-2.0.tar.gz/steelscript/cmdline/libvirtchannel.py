# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


import logging
import signal

try:
    import libvirt
    HAS_LIBVIRT = True
except:
    HAS_LIBVIRT = False

from steelscript.cmdline import exceptions, channel

# Control-u clears any entered text.  Neat.
DELETE_LINE = '\x15'

# Disconnect a session - Unix EOF.
DISCONNECT_SESSION = '\x04'

# Command terminator
ENTER_LINE = '\r'

PROMPT_PREFIX = '(^|\n|\r)'
NAME_PREFIX = '%s([-a-zA-Z0-9_.]* )?' % PROMPT_PREFIX
LOGIN_PROMPT = '%s(L|l)ogin: ' % NAME_PREFIX
# bsd password prompt does not have a trailing space.
PASSWORD_PROMPT = '%s(P|p)assword:\s*' % NAME_PREFIX
ROOT_PROMPT = '%s# ' % NAME_PREFIX

DEFAULT_EXPECT_TIMEOUT = 300


class LibVirtChannel(channel.Channel):
    """
    Channel for connecting to a serial port via libvirt.

    :param machine_name: The libvirt domain to which to connect.
    :param machine_manager_uri: The hypervisor uri where the domain
        may be found.  Defaults to a local qemu hypervisor.
    :param user: username for authentication
    :param password: password for authentication
    """

    def __init__(self, machine_name, machine_manager_uri='qemu:///system',
                 username='root', password='', **kwargs):
        """
        Manages connection and authentication via libvirt.
        """
        self._machine_name = machine_name
        self._uri = machine_manager_uri
        self._domain = None
        self._conn = None
        self._stream = None
        self._console_logged_in = False

        self._username = username
        self._password = password

    def start(self, match_res=(ROOT_PROMPT,), timeout=DEFAULT_EXPECT_TIMEOUT):
        """
        Opens a console and logs in.

        :param match_res: Pattern(s) of prompts to look for.
            May be a single regex string, or a list of them.
        :param timeout: maximum time, in seconds, to wait for a regular
            expression match. 0 to wait forever.

        :return: Python :class:`re.MatchObject` containing data on
            what was matched.
        """

        if not HAS_LIBVIRT:
            raise ImportError("Failed to import libvirt")

        if not match_res:
            match_res = [self.ROOT_PROMPT]
        elif not (isinstance(match_res, list) or isinstance(match_res, tuple)):
            match_res = [match_res, ]

        try:
            # Get connection and libvirt domain
            self._conn = libvirt.open(self._uri)
            self._domain = self._conn.lookupByName(self._machine_name)
        except libvirt.libvirtError:
            raise exceptions.ConnectionError(
                context="Failed to find domain '%s' on host" %
                        self._machine_name)

        # Make sure domain is running
        self._verify_domain_running()

        # open console
        self._stream = self._conn.newStream(0)
        console_flags = libvirt.VIR_DOMAIN_CONSOLE_FORCE
        self._domain.openConsole(None, self._stream, console_flags)

        return self._handle_init_login(match_res, timeout)

    def close(self):
        # For compatibility with other channels.
        # TODO: Should we actually close this somehow?
        pass

    def _verify_domain_running(self):
        """
        Make sure domain is running.

        :raises ConnectionError: if it is not.
        """

        info = self._domain.info()
        state = info[0]
        if state != libvirt.VIR_DOMAIN_RUNNING:
            raise exceptions.ConnectionError(
                context="Domain %s is not in running state" %
                        self._machine_name)

    def _verify_connected(self):
        # TODO: Verify that the stream is really connected.
        return self._stream is not None

    def _check_console_mode(self, logged_in_res, timeout):
        """
        Test to see if the console is logged in.

        :param logged_in_res: Regex list of logged in prompts.
        :type logged_in_res: list (single pattern not allowed)
        :param timeout: Time to wait for a prompt match.

        :return: Match object for actual prompt received.
        """
        prompt_list = [LOGIN_PROMPT, PASSWORD_PROMPT]
        prompt_list.extend(logged_in_res)

        logging.debug("Send an empty line to refresh the prompt.")
        # Clear the input buffer
        self.send('%s%s' % (DELETE_LINE, ENTER_LINE))
        (output, match) = self.expect(prompt_list, timeout=timeout)

        # If we did not get a username or password prompt, we are logged in
        if match.re.pattern not in [LOGIN_PROMPT, PASSWORD_PROMPT]:
            self._console_logged_in = True
        logging.debug("Console prompt = %s" %
                      match.string[match.start():match.end()])
        return match

    def _handle_init_login(self, logged_in_res, timeout):
        """
        Login to host console.

        :param logged_in_res: Regex list of logged in prompts.
        :type logged_in_res: list (single pattern not allowed)
        :param timeout: Time to wait for each prompt match.

        :return: Match object for last prompt received.
        """
        try:
            match = self._check_console_mode(logged_in_res,
                                             timeout=DEFAULT_EXPECT_TIMEOUT)
            if self._console_logged_in:
                return match

            # Got a password prompt
            if match.re.pattern == PASSWORD_PROMPT:
                # Do not know who was being logged in, so reset the
                # session to start over.
                logging.debug("Incomplete login session found.")
                self.send(DISCONNECT_SESSION)
                self.expect([LOGIN_PROMPT])

        except exceptions.CmdlineTimeout:
            # Make one last attempt to get a login prompt
            # Could be stuck in a program that does not have a prompt
            # we recognize.
            logging.debug("Time out logging in, retrying.")
            self.send(DISCONNECT_SESSION)
            self.expect([LOGIN_PROMPT])

        # Now do the login.
        self.send('%s%s' % (self._username, ENTER_LINE))
        (output, match) = self.expect([PASSWORD_PROMPT, ROOT_PROMPT])
        if match.re.pattern == PASSWORD_PROMPT:
            self.send('%s%s' % (self._password, ENTER_LINE))
            (output, match) = self.expect(logged_in_res)
        self._console_logged_in = True
        return match

    def receive_all(self):
        """
        Returns all text currently in the receive buffer, effectively flushing
        it.

        :return: the text that was present in the receive queue, if any.
        """
        # Enclosed variables are immutable, but their contents are not.
        received = ['']

        def handler(s, buf, opaque):
            received[0] += buf.decode('utf8', 'ignore')

        self._stream.recvAll(handler, None)
        return received[0]

    def send(self, text_to_send):
        """
        Sends text to the channel immediately.  Does not wait for any response.

        :param str text_to_send: Text to send, including command terminator(s)
                             when applicable.
        """
        # There is also a sendAll that works like recvAll, but while
        # Python libvirt's recv still needs a length specified, its send
        # just takes the length of the supplied data automatically.
        encoded = text_to_send.encode('utf8')
        self._stream.send(encoded)

    def expect(self, match_res, timeout=DEFAULT_EXPECT_TIMEOUT):
        """
        Matches regular expressions against singles lines in the stream.

        Internally, this method works with bytes, but input and output
        are unicode as usual.

        :param match_res: a list of regular expressions to match against
            the output.
        :param timeout: Time to wait for matching data in the stream,
            in seconds.  Note that the default timeout is longer than
            on most channels.

        :return: ``(output, match_object)`` where output is the output of
            the command (without the matched text), and match_object is a
            Python :class:`re.MatchObject` containing data on what was matched.

            You may use ``MatchObject.string[m.start():m.end()]`` to recover
            the actual matched text, which will be unicode.

            ``re.MatchObject.pattern`` will contain the pattern that matched,
            which will be one of the elements of match_res passed in.

        :raises CmdlineTimeout: if no match found before timeout.
        """

        # Timeout handler
        def expectsig(signum, frame):
            raise exceptions.CmdlineTimeout(timeout)

        match_res, safe_match_text = self._expect_init(match_res)

        # We want to manage lines as unicode so that match object results
        # will be stored as unicode.  Otherwise, we lead bytestrings
        # out to the caller.  The type of the matched string is determined
        # by the input string- the regex pattern can be either bytes
        # or unicode.
        data = ""
        signal.signal(signal.SIGALRM, expectsig)
        signal.alarm(timeout)
        while True:
            recv = self._stream.recv(1)
            data = data + recv.decode('utf8', 'ignore')
            match = self._find_match(data, match_res)
            if match is not None:
                logline = data
                logging.debug('> ' + logline.strip('\r\n'))
                logging.debug("successfully matched %s", match.re.pattern)
                signal.alarm(0)
                return (data[0:match.start()], match)

            if recv == b'\n':
                # Consoles will send either an 8 bit codec UTF-8
                # Not 7 bit ASCII.  Use UTF-8 as that includes ISO-8859-1
                # which should work for anything we have.
                logline = data.strip('\r\n')
                logging.debug('> ' + logline)
