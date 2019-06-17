# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


import re

from steelscript.cmdline import cli, exceptions


class IOS_CLI(cli.CLI):

    """
    Implementation of a CLI for IOS devices.
    """

    NAME_PREFIX_RE = r'(^|\n|\r)(?P<name>(\S+\-)?t[a-zA-Z0-9_\-]+)'

    CLI_NORMAL_PROMPT = NAME_PREFIX_RE + '>'
    CLI_ENABLE_PROMPT = NAME_PREFIX_RE + '#'
    CLI_CONFIG_PROMPT = NAME_PREFIX_RE + r'\(config\)#'
    CLI_SUBIF_PROMPT = NAME_PREFIX_RE + r'\(config-subif\)#'
    CLI_ANY_PROMPT = NAME_PREFIX_RE + r'(>|#|\(config\)#|\(config-subif\)#)'

    # CLI_START_PROMPT is needed by base CLI class for the first
    # prompt expected on login to device. Either telnet or ssh.
    CLI_START_PROMPT = CLI_NORMAL_PROMPT
    CLI_ERROR_PROMPT = r'(\s+)?(\^|%)'

    def start(self):
        """
        Initialize underlying channel.
        """
        super(IOS_CLI, self).start(start_prompt=self.CLI_START_PROMPT)

        # Disable paging
        self._disable_paging()

    def _disable_paging(self):
        """
        Disable session paging.

        When we run a CLI command, we want to get all output instead of
        a page at a time.
        """
        self._log.debug('Disabling paging on IOS')
        self._send_line_and_wait('terminal length 0', self.CLI_NORMAL_PROMPT)

    def current_cli_mode(self):
        """
        Determine the current mode of the CLI.

        Sends a newline and checks which prompt pattern matches.

        :return: current CLI mode.
        :raises UnknownCLIMode: if the current mode could not be detected.
        """

        (output, match_res) = self._send_line_and_wait('',
                                                       [self.CLI_NORMAL_PROMPT,
                                                        self.CLI_ENABLE_PROMPT,
                                                        self.CLI_CONFIG_PROMPT,
                                                        self.CLI_SUBIF_PROMPT])

        modes = {self.CLI_NORMAL_PROMPT: cli.CLIMode.NORMAL,
                 self.CLI_ENABLE_PROMPT: cli.CLIMode.ENABLE,
                 self.CLI_CONFIG_PROMPT: cli.CLIMode.CONFIG,
                 self.CLI_SUBIF_PROMPT: cli.CLIMode.SUBIF}

        if match_res.re.pattern not in modes:
            raise exceptions.UnknownCLIMode(prompt=output)
        return modes[match_res.re.pattern]

    def enter_mode(self, mode=cli.CLIMode.CONFIG, interface=None):
        """
        Enter mode based on mode string ('normal', 'enable', or 'configure').

        :param mode: The CLI mode to enter. It must be 'normal', 'enable', or
                   'configure'
        :param interface: If entering sub-if mode, interface to enter

        :raises UnknownCLIMode: if mode is not "normal", "enable", or
                                "configure"
        """
        if mode == cli.CLIMode.NORMAL:
            self.enter_mode_normal()

        elif mode == cli.CLIMode.ENABLE:
            self.enter_mode_enable()

        elif mode == cli.CLIMode.CONFIG:
            self.enter_mode_config()

        elif mode == cli.CLIMode.SUBIF:
            self.enter_mode_subif(interface)

        else:
            raise exceptions.UnknownCLIMode(mode=mode)

    def enter_mode_normal(self):
        """
        Puts the CLI into the 'normal' mode (its initial state).

        Note this will go 'backwards' if needed (e.g., exiting config mode)

        :raises UnknownCLIMode: if mode is not "normal", "enable", or
            "configure"
        """

        self._log.debug('Going to normal mode')

        mode = self.current_cli_mode()

        if mode == cli.CLIMode.NORMAL:
            self._log.debug('Already at normal, doing nothing')

        elif mode == cli.CLIMode.ENABLE:
            self._send_line_and_wait('disable', self.CLI_NORMAL_PROMPT)

        elif mode == cli.CLIMode.CONFIG:
            self._send_line_and_wait('end', self.CLI_ENABLE_PROMPT)
            self._send_line_and_wait('disable', self.CLI_NORMAL_PROMPT)

        elif mode == cli.CLIMode.SUBIF:
            self._send_line_and_wait('end', self.CLI_ENABLE_PROMPT)
            self._send_line_and_wait('disable', self.CLI_NORMAL_PROMPT)

        else:
            raise exceptions.UnknownCLIMode(mode=mode)

    def enter_mode_enable(self):
        """
        Puts the CLI into enable mode.

        Note this will go 'backwards' if needed (e.g., exiting config mode)

        :raises UnknownCLIMode: if mode is not "normal", "enable", or
            "configure"
        """

        self._log.debug('Going to Enable mode')

        mode = self.current_cli_mode()

        if mode == cli.CLIMode.NORMAL:
            self._enable()

        elif mode == cli.CLIMode.ENABLE:
            self._log.debug('Already at Enable, doing nothing')

        elif mode == cli.CLIMode.CONFIG:
            self._send_line_and_wait('end', self.CLI_ENABLE_PROMPT)

        elif mode == cli.CLIMode.SUBIF:
            self._send_line_and_wait('end', self.CLI_ENABLE_PROMPT)

        else:
            raise exceptions.UnknownCLIMode(mode=mode)

    def _enable(self):
        """
        Puts the CLI in enable mode.  This may or may not require a password.
        """
        password_prompt = r'(P|p)assword:'
        (output, match_res) = self._send_line_and_wait('enable',
                                                       [self.CLI_ENABLE_PROMPT,
                                                        password_prompt])
        if match_res.re.pattern == password_prompt:
            self._send_line_and_wait(self._password, self.CLI_ENABLE_PROMPT)

    def enter_mode_config(self):
        """
        Puts the CLI into config mode, if it is not there already.

        :raises UnknownCLIMode: if mode is not "normal", "enable", or
            "configure"
        """

        self._log.debug('Going to Config mode')

        mode = self.current_cli_mode()

        if mode == cli.CLIMode.NORMAL:
            self._enable()
            self._send_line_and_wait('config terminal', self.CLI_CONFIG_PROMPT)

        elif mode == cli.CLIMode.ENABLE:
            self._send_line_and_wait('config terminal', self.CLI_CONFIG_PROMPT)

        elif mode == cli.CLIMode.CONFIG:
            self._log.debug('Already at Config, doing nothing')

        elif mode == cli.CLIMode.SUBIF:
            self._send_line_and_wait('exit', self.CLI_CONFIG_PROMPT)

        else:
            raise exceptions.UnknownCLIMode(mode=mode)

    def enter_mode_subif(self, interface):
        """
        Puts the CLI into sub-interface mode, if it is not there already.
        """

        self._log.debug('Going to sub-if mode')
        if interface is None:
            raise ValueError('Cannot enter_mode_subif with Interface None')
        # enter mode config
        self.enter_mode(cli.CLIMode.CONFIG)

        # enter sub-interface
        self._send_line_and_wait(
            "interface %s" %
            interface,
            self.CLI_SUBIF_PROMPT)

    def exec_command(self, command, timeout=60, mode=cli.CLIMode.CONFIG,
                     output_expected=None, error_expected=False,
                     interface=None, prompt=None):
        """Executes the given command.

        This method handles detecting simple boolean conditions such as
        the presence of output or errors.

        :param command:  command to execute, newline appended automatically
        :param timeout:  maximum time, in seconds, to wait for the command to
            finish. 0 to wait forever.
        :param mode:  mode to enter before running the command.  To skip this
            step and execute directly in the cli's current mode, explicitly
            set this parameter to None.  The default is "configure"
        :param output_expected: If not None, indicates whether output is
            expected (True) or no output is expected (False).
            If the opposite occurs, raise UnexpectedOutput. Default is None.
        :type output_expected: bool or None
        :param error_expected: If true, cli error output (with a leading '%')
            is expected and will be returned as regular output instead of
            raising a CLIError.  Default is False, and error_expected always
            overrides output_expected.
        :type error_expected: bool
        :param interface: if mode 'subif', interface to configure 'gi0/1.666'
            or 'vlan 691'
        :type interface: string
        :param prompt: Prompt regex for matching unusual prompts.  This should
            almost never be used as the ``mode`` parameter automatically
            handles all typical cases.  This parameter is for unusual
            situations like the install config wizard.

        :raises CmdlineTimeout: on timeout
        :raises CLIError: if the output matches the cli's error format, and
            error output was not expected.
        :raises UnexpectedOutput: if output occurs when no output was
            expected, or no output occurs when output was expected

        :return: output of the command, minus the command itself.
        """

        if output_expected is not None and not isinstance(
                output_expected, bool):
            raise TypeError("exec_command: output_expected requires a boolean "
                            "value or None")

        if mode is not None:
            self.enter_mode(mode, interface)

        self._log.debug('Executing cmd "%s"' % command)

        if prompt is None:
            prompt = self.CLI_ANY_PROMPT
        (output, match_res) = self._send_line_and_wait(command,
                                                       prompt,
                                                       timeout=timeout)

        output = '\n'.join(output.splitlines()[1:])

        if output and (re.match(self.CLI_ERROR_PROMPT, output)):
            if error_expected:
                # Skip output_expected processing entirely.
                return output
            else:
                try:
                    mode = self.current_cli_mode()
                except exceptions.UnknownCLIMode:
                    mode = '<unrecognized>'
                raise exceptions.CLIError(command, output=output, mode=mode)

        if ((output_expected is not None) and (bool(output) !=
                                               bool(output_expected))):
            raise exceptions.UnexpectedOutput(command=command,
                                              output=output,
                                              expected_output=output_expected)
        return output
