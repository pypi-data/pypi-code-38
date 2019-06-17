# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import logging

from steelscript.cmdline import sshchannel
from steelscript.cmdline import exceptions
from steelscript.common.connection import test_tcp_conn

# Control-u clears any entered text.  Neat.
DELETE_LINE = '\x15'

# Command terminator
ENTER_LINE = '\r'

# Local qemu (KVM) hypervisor.
DEFAULT_MACHINE_MANAGER_URI = 'qemu:///system'


class CLIMode(object):
    """
    Different config modes a CLI can be in.  Not all CLIs support all modes.
    """

    SHELL = 'shell'
    """OS shell instead of CLI"""

    NORMAL = 'normal'
    """Default mode in which the CLI starts"""

    ENABLE = 'enable'
    """Enable some additional commands"""

    CONFIG = 'configure'
    """Config mode; enables all commands"""

    SUBIF = 'subif'
    """Subinterface command mode"""

    UNDEF = ''
    """Used within the code to indicate unknown or don`t-care situations"""


class CLI(object):
    """
    Base class CLI implementation for Network Devices

    Vendor specific CLIs can inherit from this base class. This class by
    itself will try to work on a generic CLI if vendor specific class is not
    present.

    For the "should match any prompt" regular expressions, the focus was
    mostly on common OSes in Riverbed's internal environment.  Other systems
    may require subclassing this class and overriding the prompt regexes.

    :param host: host/ip
    :type hostname: string
    :param user: username to log in with
    :type username: string
    :param password: password to log in with
    :type password: string
    :param private_key_path: absolute path to RSA private key,
        used instead of password
    :type private_key_path: string
    :param terminal:  terminal emulation to use; default to 'console'
    :type terminal: string
    :param prompt: A prompt to match.  Defaults to :const:`CLI_ANY_PROMPT`
    :type prompt: regex pattern
    :param transport_type: *DEPRECATED* (use ``channel_class``): telnet or ssh,
        defaults to ssh
    :type transport_type: string
    :param user: *DEPRECATED* (use ``username``)
    :param host: *DEPRECATED* (use ``hostname``)
    :param channel_class: Class object to instantiate for persistent
        communication.  Defaults to
        ``steelscript.cmdline.sshchannel.SSHChannel``
    :type channel_class: class
    :param channel_args: additional ``transport_type``-dependent
        arguments, passed blindly to the transport ``start`` method.
    """

    CLI_START_PROMPT = r'(^|\n|\r)(\[?\S+\s?\S+\]?)(#|\$|>|~)(\s)?$'
    """A regex suitable for most initial CLI prompts, root or non-root"""

    CLI_ROOT_PROMPT = r'(^|\n|\r)(\[?\S+\s?\S+\]?)(#)(\s)?$'
    """A regex intended for use with POSIX prompts for root ending in '#'"""

    CLI_ANY_PROMPT = CLI_START_PROMPT
    """
    A regex that is suitable for most CLIs, root or regular user.

    Note that this does not specifically check hostnames, which might
    lead to false positive matches.
    """

    def __init__(self, hostname=None, username='admin', password=None,
                 private_key_path=None,
                 terminal='console', prompt=None, port=None,
                 machine_name=None,
                 machine_manager_uri=DEFAULT_MACHINE_MANAGER_URI,
                 channel_class=sshchannel.SSHChannel, **channel_args):

        self._channel_class = channel_class
        self._channel_args = dict()
        self._channel_args['hostname'] = hostname
        self._channel_args['username'] = username
        self._channel_args['password'] = password
        self._channel_args['private_key_path'] = private_key_path
        self._channel_args['terminal'] = terminal
        self._channel_args['machine_name'] = machine_name
        self._channel_args['machine_manager_uri'] = machine_manager_uri
        self._channel_args['prompt'] = prompt

        # Some channels do their own defaulting of the port number.
        # Don't squash it by explicitly passing None.
        if port is not None:
            self._channel_args['port'] = port

        self._channel_args.update(channel_args)

        self._log = logging.getLogger(__name__)
        self._prompt = prompt
        self._default_mode = None
        if self._prompt is None:
            self._prompt = self.CLI_ANY_PROMPT

        self.channel = None

    def __del__(self):
        self._cleanup_helper()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self._cleanup_helper()

    def _cleanup_helper(self):
        if self.channel:
            self.channel.close()
        self.channel = None

    def start(self, start_prompt=None):
        """
        Initialize underlying channel.

        :param start_prompt: A non-default prompt to match, if any.
        :type start_prompt: regex pattern
        """

        self.channel = self._channel_class(**self._channel_args)

        # Wait for a prompt, try and figure out where we are.  It's a new
        # channel so we should only be at bash or the main CLI prompt.
        if start_prompt is None:
            start_prompt = self.CLI_START_PROMPT

        host = self._channel_args['hostname']
        port = self._channel_args.get('port', self.channel.conn_port)
        # will raise an exception if it fails.
        if test_tcp_conn(host, port):
            self._log.info("test_tcp_conn to {0}:{1} passed"
                           "".format(host, port))
            self.channel.start(start_prompt)

    def _send_and_wait(self, text_to_send, match_res, timeout=60):
        """
        Flushes the buffer, sends data and waits for a match to the patterns.

        :param text_to_send: Text to send, may be empty.  Note, you are
            responsible for your own command terminator!
        :param match_res: Pattern(s) to look for to be considered successful.
        :param timeout: Maximum time, in seconds, to wait for a regular
            expression match. 0 to wait forever.

        :return: ``(output, match_object)`` where output is the output of the
            command (without the matched text), and match_object is a Python
            :class:`re.MatchObject` containing data on what was matched.
        """
        # TODO: There was a call to 'self.channel.receive_all()' here, which
        # appears to be used to 'flush' the buffer first.  For interactive
        # prompts on libvirtchannel, this was causing an endless blocking call.
        # We still probably want to figure out an alternative.

        # will raise an exception if it fails.
        if test_tcp_conn(self._channel_args['hostname'],
                         self._channel_args.get('port',
                                                self.channel.conn_port)):
            self.channel.send(text_to_send)
            return self.channel.expect(match_res, timeout)

    def _send_line_and_wait(self, text_to_send, match_res, timeout=60):
        """
        Same as `_send_and_wait` but appends a line terminator first.

        :param text_to_send: Text to send, may be empty.
        :param match_res: Pattern(s) to look for to be considered successful.
        :param timeout: Maximum time, in seconds, to wait for a regular
            expression match. 0 to wait forever.

        :return: ``(output, match_object)`` where output is the output of the
            command (without the matched text), and match_object is a Python
            :class:`re.MatchObject` containing data on what was matched.
        """
        text_to_send = text_to_send + ENTER_LINE
        return self._send_and_wait(text_to_send, match_res, timeout)

    def exec_command(self, command, timeout=60, output_expected=None,
                     prompt=None):
        """
        Executes the given command.

        This method handles detecting simple boolean conditions such as
        the presence of output or errors.

        :param command:  command to execute, newline appended automatically
        :param timeout:  maximum time, in seconds, to wait for the command to
            finish. 0 to wait forever.
        :param output_expected: If not None, indicates whether output is
            expected (True) or no output is expected (False).
            If the opposite occurs, raise UnexpectedOutput. Default is None.
        :type output_expected: bool or None
        :param prompt: Prompt regex for matching unusual prompts.  This should
            almost never needed.  This parameter is for unusual
            situations like an install config wizard.

        :return: output of the command, minus the command itself.

        :raises TypeError: if output_expected type is incorrect
        :raises CmdlineTimeout: on timeout
        :raises UnexpectedOutput: if output occurs when no output was
            expected, or no output occurs when output was expected
        """

        if output_expected not in (True, False, None):
            raise TypeError("exec_command: output_expected requires a boolean "
                            "value or None")

        self._log.debug('Executing cmd "%s"' % command)

        if prompt is None:
            prompt = self._prompt
        (output, match) = self._send_line_and_wait(command,
                                                   prompt,
                                                   timeout=timeout)

        # CLI adds on escape chars and such sometimes, so to remove the
        # command we just send from the output, split the output into lines,
        # then rejoin it with the first line removed.
        output = '\n'.join(output.splitlines()[1:])

        if ((output_expected is not None) and (bool(output) !=
                                               bool(output_expected))):
            raise exceptions.UnexpectedOutput(command=command,
                                              output=output,
                                              expected_output=output_expected)
        return output


# Note that CLICache must be defined after CLI in order to use the CLI
# class object in a default parameter.
class CLICache(object):
    """
    The CLI cache helps minimize open CLIs per system.

    Leaving multiple CLI sessions open on some system, most notably the
    Riverbed appliance CLI, can result in performance degradation
    or even out-of-memory conditions.  This cache allows for sharing
    a single CLI and easily cleaning up all CLIs on all systems.
    """

    @staticmethod
    def attach_cache(target):
        """
        Add a CLI cache to the target as a data member.

        This is for use in dynamic loading systems, and not for general
        consumption.  Just assign the result of CLICache() the normal
        way in typical code.
        """
        target.cli_cache = CLICache()

    def __init__(self):
        self._cli_cache = {}

    def get_cli(self, resource, cli_class=CLI):
        """Get CLI from cache, or cache a new one. """
        if resource.uniqueid not in self._cli_cache:
            # TODO: IP discovery may need to happen here.
            #       For now, assume hostname or admin_ip is known.
            try:
                host = resource.admin_ip
            except IndexError as e:
                logging.debug("Failed to get admin ip: %s" % e)
                logging.debug("Use hostname instead.")
                host = resource.hostname
            cli = cli_class(host=host,
                            user=resource.username,
                            password=resource.password)
            cli.start()
            self._cli_cache[resource.uniqueid] = cli
        return self._cli_cache[resource.uniqueid]

    def drop_cli(self, resource):
        """
        Removes the cli from the cache, allowing it to close.

        If another reference is held elsewhere, the next call
        to `get_cli` will result in multiple open CLI sessions.
        """

        try:
            del self._cli_cache[resource.uniqueid]
        except KeyError:
            pass

    def drop_all(self):
        """Clean up CLI cache, disconnecting all sessions"""
        self._cli_cache.clear()
