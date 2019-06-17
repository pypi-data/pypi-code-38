# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.
from __future__ import (absolute_import, unicode_literals, print_function,
                        division)

import re

from steelscript.cmdline import exceptions
from steelscript.cmdline import cli


class VyattaCLI(cli.CLI):

    """
    Provides an interface to interact with the CLI of a vyatta router
    """

    # Vyatta prompts are of the following format:
    # 'user vyatta' login : "vyatta@vyatta6:~$"
    # this might change later on

    NAME_PREFIX_RE = r'(?P<user>[a-zA-Z][a-zA-Z0-9_\-]*)'
    NAME_PREFIX_RE += r'@(?P<name>[a-zA-Z0-9_\-.]+)'

    # Vyatta prompt terminator is as follows
    # For 'root' users:
    # * normal mode: "root@vyatta6:~# "
    # * config mode: "root@vyatta6# "
    #
    # For 'vyatta', non root users:
    # * normal mode: "vyatta@vyatta6:~$ "
    # * config mode: "vyatta@vyatta6#"

    CLI_NORMAL_PROMPT = NAME_PREFIX_RE + r':~[\$|#]'
    CLI_CONFIG_PROMPT = NAME_PREFIX_RE + '#'
    CLI_ANY_PROMPT = [CLI_NORMAL_PROMPT, CLI_CONFIG_PROMPT]

    # CLI_START_PROMPT is needed by base CLI class for the first
    # prompt expected on login to device. Either telnet or ssh.
    CLI_START_PROMPT = CLI_NORMAL_PROMPT

    # add error prompts to this variable
    CLI_ERROR_PROMPT = '^Cannot'

    # Line to be discarded from CLI output
    DISCARD_PROMPT = '[edit]'

    def start(self):
        """
        Initialize underlying channel.

        Vyatta transport channel is presently configured to SSH only.
        There is no limitation for this, Vyatta could be configured
        for telnet as well, but that would involve additional config
        on Vyatta bring up during install. Ignoring for now.
        """
        super(VyattaCLI, self).start(start_prompt=self.CLI_START_PROMPT)

        # Disable paging
        self._disable_paging()

    def _disable_paging(self):
        """
        Disable session paging.

        When we run a CLI command, we want to get all output instead of
        a page at a time.
        """
        self._log.debug('Disabling paging on Vyatta')
        self._send_line_and_wait(
            'set terminal length 0',
            self.CLI_NORMAL_PROMPT)

    def current_cli_mode(self):
        """
        Determine the current mode of the CLI.

        This is done by sending newline and check which prompt pattern matches.

        :return: current CLI mode.
        :raises UnknownCLIMode: if the current mode could not be detected.
        """

        (output, match) = self._send_line_and_wait('',
                                                   [self.CLI_NORMAL_PROMPT,
                                                    self.CLI_CONFIG_PROMPT, ])

        modes = {self.CLI_NORMAL_PROMPT: cli.CLIMode.NORMAL,
                 self.CLI_CONFIG_PROMPT: cli.CLIMode.CONFIG, }

        if match.re.pattern not in modes:
            raise exceptions.UnknownCLIMode(prompt=output)
        return modes[match.re.pattern]

    def enter_mode(self, mode=cli.CLIMode.CONFIG, force=False):
        """
        Enter the mode based on mode string ('normal','config').

        :param mode: The CLI mode to enter. It must be 'normal', 'enable', or
            'configure'
        :type mode: string

        :param force: Discard commits and force enter requested mode
        :type force: Boolean

        :raises UnknownCLIMode: if mode is not "normal", "configure"
        """
        if mode == cli.CLIMode.NORMAL:
            self.enter_mode_normal(force)

        elif mode == cli.CLIMode.CONFIG:
            self.enter_mode_config()

        else:
            raise exceptions.UnknownCLIMode(mode=mode)

    def enter_mode_normal(self, force=False):
        """
        Puts the CLI into the 'normal' mode.

        In this mode you can run commands, but you cannot change
        the configuration.

        :param force: Will force enter 'normal' mode, discarding all changes
            that haven't been committed.
        :type force: Boolean

        :raises CLIError: if unable to go from "configure" mode to "normal"
            This happens if "commit" is not applied after config changes
        :raises UnknownCLIMode: if mode is not "normal" or "configure"
        """

        self._log.info('Going to normal mode')
        mode = self.current_cli_mode()

        if mode == cli.CLIMode.NORMAL:
            self._log.debug('Already at normal, doing nothing')

        elif mode == cli.CLIMode.CONFIG:
            if force:
                self._log.debug('Entering normal mode, discarding all commits')
                self._send_line_and_wait(
                    'exit discard',
                    self.CLI_NORMAL_PROMPT)

            else:
                self._log.debug('Entering normal mode')
                (output, match_res) = self._send_line_and_wait(
                    'exit', [self.CLI_ERROR_PROMPT, self.CLI_NORMAL_PROMPT])

                if re.match(self.CLI_ERROR_PROMPT, match_res.string):
                    raise exceptions.CLIError(
                        command="exit", output=match_res.string, mode=mode)
        else:
            raise exceptions.UnknownCLIMode(mode=mode)

    def enter_mode_config(self):
        """
        Puts the CLI into config mode, if it is not there already.

        In this mode, you can make changes in the configuration.

        :raises UnknownCLIMode: if mode is not "normal", "configure"
        """

        self._log.debug('Going to Config mode')

        mode = self.current_cli_mode()

        if mode == cli.CLIMode.NORMAL:
            self._send_line_and_wait('configure', self.CLI_CONFIG_PROMPT)
        elif mode == cli.CLIMode.CONFIG:
            self._log.debug('Already at Config, doing nothing')
        else:
            raise exceptions.UnknownCLIMode(mode=mode)

    def exec_command(self, command, timeout=60, mode=cli.CLIMode.CONFIG,
                     force=False, output_expected=None, prompt=None):
        """
        Executes the given command.

        This method handles detecting simple boolean conditions such as
        the presence of output or errors.

        :param command:  command to execute, newline appended automatically
        :param timeout:  maximum time, in seconds, to wait for the command to
            finish. 0 to wait forever.
        :param mode:  mode to enter before running the command.  To skip this
            step and execute directly in the cli's current mode, explicitly
            set this parameter to None.  The default is "configure"
        :param force: Will force enter mode, discarding all changes
                     that haven't been committed.
        :type force: Boolean
        :param output_expected: If not None, indicates whether output is
            expected (True) or no output is expected (False).
            If the opposite occurs, raise UnexpectedOutput. Default is None.
        :type output_expected: bool or None
        :param prompt: Prompt regex for matching unusual prompts.  This should
            almost never be used as the ``mode`` parameter automatically
            handles all typical cases.  This parameter is for unusual
            situations like the install config wizard.

        :return: output of the command, minus the command itself.

        :raises TypeError: if output_expected type is incorrect
        :raises CmdlineTimeout: on timeout
        :raises UnexpectedOutput: if output occurs when no output was
            expected, or no output occurs when output was expected
        """
        if output_expected is not None and not isinstance(
                output_expected, bool):
            raise TypeError("exec_command: output_expected requires a boolean "
                            "value or None")
        if mode is not None:
            self.enter_mode(mode, force)

        self._log.debug('Executing cmd "%s"' % command)

        if prompt is None:
            prompt = self.CLI_ANY_PROMPT
        (output, match_res) = self._send_line_and_wait(command,
                                                       prompt,
                                                       timeout=timeout)
        output = output.splitlines()[1:]

        # Vyatta does not have a standard error prompt
        # In config mode, each command (erroneous or not) is
        # followed with '[edit]'. This skews the result for
        # output_expected flag

        # To address this remove line with '[edit]' when in config mode

        if mode == cli.CLIMode.CONFIG:
            output = [line for line in output if self.DISCARD_PROMPT != line]

        output = '\n'.join(output)

        if ((output_expected is not None) and (bool(output) !=
                                               bool(output_expected))):
            raise exceptions.UnexpectedOutput(command=command,
                                              output=output,
                                              expected_output=output_expected)
        return output
