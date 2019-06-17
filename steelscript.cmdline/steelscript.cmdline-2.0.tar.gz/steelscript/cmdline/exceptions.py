# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from __future__ import (absolute_import, unicode_literals, print_function,
                        division)

from pprint import pformat

from steelscript.common import exceptions


class CmdlineException(exceptions.RvbdException):
    """
    Base exception representing an error executing the command line.

    :param command: The command that produced the error.
    :param output: The output returned, possibly None.

    :ivar command: The command that produced the error.
    :ivar output: The output returned.  None if the command did not return.
    """

    def __init__(self, command=None, output=None, _subclass_msg=None):
        self.command = command
        self.output = output
        if _subclass_msg is None:
            if output is None:
                if command is None:
                    msg = 'Unknown command line error'
                else:
                    msg = (("Command '%s' encountered an unknown error, "
                            "with no output.") % command)
            else:
                msg = ("Command '%s' encountered an error, with output '%s'" %
                       (command, output))
        else:
            msg = _subclass_msg
        super(CmdlineException, self).__init__(msg)

    def _process_failed_match(self, failed_match):
        # Take a failed match, which may be a match result object, a pattern
        # object, or just a string, and pull the string out of it.
        # Or it can be a list of the above types.
        # Returns a tuple of the string and either an empty string or a
        # " while waiting for %s" string suitable for including in an error.

        if isinstance(failed_match, list) and len(failed_match) == 1:
            failed_match = failed_match[0]

        if failed_match is None:
            failed_match_pattern = None
        elif isinstance(failed_match, list):
            failed_match_pattern = (
                "one of:\n%s\n" %
                pformat([self._convert_match(p) for p in failed_match],
                        indent=2))
        else:
            failed_match_pattern = "'%s'" % self._convert_match(failed_match)

        if failed_match is None:
            match_msg = ''
        else:
            match_msg = (" while waiting to match %s" %
                         failed_match_pattern)
        return failed_match_pattern, match_msg

    def _convert_match(self, match):
        if hasattr(match, 're'):
            return match.re.pattern
        elif hasattr(match, 'pattern'):
            return match.pattern
        else:
            return match


class CmdlineTimeout(CmdlineException):
    """
    Indicates a command was abandoned due to a timeout.

    Some timeouts within a given protocol may be reported as ConnectionError
    as the third-party libraries are not always specific about causes.
    However, all timeouts triggered in SteelScript code will raise this
    exception.

    :param timeout: The number of seconds that we were waiting for.
    :param command: The command we were trying to execute.
    :param output: Partial output received, if any.
    :param failed_match: What we were trying to match, or None.
    :type failed_match: Match object, pattern object, or string.

    :ivar command: The command we were trying to execute.
    :ivar output: Partial output received, if any.
    :ivar timeout: The number of seconds that we were waiting for.
    :ivar failed_match_pattern: The pattern we were trying to match, if any.
    """

    def __init__(self, timeout, command=None, output=None, failed_match=None):
        self.timeout = timeout
        self.failed_match_pattern, match_msg = (
            self._process_failed_match(failed_match))

        msg = ("Command '%s' timed out%s after %d seconds." %
               (command, match_msg, timeout))

        super(CmdlineTimeout, self).__init__(command, _subclass_msg=msg)


class ConnectionError(CmdlineException):
    """
    Indicates a (probably) non-timeout error from the underlying protocol.

    May contain a wrapped exception from a third-party library.
    In Python 3 this would be on the __cause__ attribute.
    The third-party library may not use a specific exception for timeouts,
    so certain kinds of timeouts may appear as a ConnectionError.
    Timeouts managed by SteelScript code should use CmdlineTimeout instead.

    This exception should be used to propagate errors up to levels
    that should not be aware of the specific underlying protocol.

    :param command: The command we were trying to execute.
    :param output: Any output produced just before the failure.
    :param cause: The protocol-specific exception, if any, that triggered this.
    :param failed_match: What we were trying to match, or None.
    :type failed_match: Match object, pattern object, or string.
    :param context: An optional string describing the context of the error.

    :ivar command: The command we were trying to execute.
    :ivar output: Any output produced just before the failure.
    :ivar cause: The protocol-specific exception, if any, that triggered this.
    :ivar failed_match_pattern: The pattern we were trying to match, if any.
    """

    def __init__(self, command=None, output=None, cause=None,
                 failed_match=None, context=None, _subclass_msg=None):
        self.cause = cause
        if _subclass_msg is None:
            if command:
                msg = "Connection error while executing '%s'" % command
            else:
                msg = "Connection error."
            if context is not None:
                msg = "%s\n    Additional context: '%s'" % (msg, context)
            if cause is not None:
                msg = "%s\n    Underlying exception:\n%s" % (msg, cause)

            self.failed_match_pattern, match_msg = (
                self._process_failed_match(failed_match))
            if match_msg:
                msg = "%s%s" % (msg, match_msg)
        else:
            msg = _subclass_msg
        super(ConnectionError, self).__init__(command, _subclass_msg=msg)


class CLINotRunning(ConnectionError):
    """
    Exception for when the CLI has crashed or could not be started.

    :param output: Output of trying to start the CLI, or None if
                   we expected the CLI to be there and it was not.

    :ivar output:  Output of trying to start the CLI, or None if we expected
                   the CLI to be there and it was not.
    """

    def __init__(self, output=None):
        if output is None:
            msg = "CLI is not running."
        else:
            msg = "Could not start the CLI: '%s'" % output
        super(CLINotRunning, self).__init__(command=None, output=output,
                                            _subclass_msg=msg)


class CmdlineError(CmdlineException):
    """
    Base for command responses that specifically indicate an error.

    See specific exceptions such as ``ShellError`` and ``CLIError`` for
    additional debugging fields.
    """
    pass


class ShellError(CmdlineError):
    """
    Exception representing a nonzero exit status from the shell.

    Technically, representing an unexpected exit from the shell, as some
    command, such as diff, have successful nonzero exits.

    :param command: The command that produced the error.
    :param exit_status: The exit status of the command.
    :param output: The output as returned by the shell, if any.

    :ivar command: The command that produced the error.
    :ivar exit_status: The exit status of the command.
    :ivar output: The output as returned by the shell, if any.
    """

    def __init__(self, command, exit_status, output=None):
        self.exit_status = exit_status
        msg = ("Command '%s exited with status %d, output: '%s'" %
               (command, exit_status,
                '<no output>' if output is None else output))
        super(ShellError, self).__init__(command, output=output,
                                         _subclass_msg=msg)


class CLIError(CmdlineError):
    """
    Exception representing an error message from the CLI.

    :param command: The command that produced the error.
    :param mode: The CLI mode we were in when the error occurred.
    :param output: The error string as returned by the CLI.

    :ivar command: The command that produced the error.
    :ivar mode: The CLI mode we were in when the error occurred.
    :ivar output: The error string as returned by the CLI.
    """

    def __init__(self, command, mode, output=None):
        self.mode = mode
        msg = ("Command '%s' in mode '%s' resulted in an error: '%s'" %
               (command, mode, '<no output>' if output is None else output))
        super(CLIError, self).__init__(command,
                                       output=output, _subclass_msg=msg)


class UnexpectedOutput(CmdlineException):
    """Exception for when output does not match expectations.

    This could include output where none was expected, no output where
    some was expected, or differing output than expected.

    This generally does not mean easily detectable error output, which is
    indicated by the appropriate subclass of ``CmdlineError``

    :param command: The command that produced the error.
    :param output: The output as returned from the command, possibly None.
    :param expected_output: The output expected from the command,
          possibly None.  If unspecified output was expected, set to True.
    :param notes: Some extra information related with the error, possibly None.
    :type expected_output: String, possibly a regexp pattern.
    :type notes: List of strings

    :ivar command: The command that produced the error.
    :ivar output: The output as returned from the command.
    :ivar expected_output: The output expected from the command, possibly None.
                           If unspecified output was expected, set to True.
    :ivar notes: Some extra information related with the error, possibly None.
    :type expected_output: String, possibly a regexp pattern.
    :type notes: List of strings
    """

    def __init__(self, command, output, expected_output=None, notes=None):
        self.expected_output = expected_output

        if output:
            msg = ("Command '%s' returned the following output:\n%s\n" %
                   (command, output))
        else:
            msg = "Command '%s' returned no output " % command

        if expected_output is True:
            msg = "%s%s" % (msg, "where unspecified output was expected.")
        elif expected_output:
            msg = ("%s%s%s" %
                   (msg, "where this output was expected:\n", expected_output))
        else:
            msg = "%s%s" % (msg, "where none was expected.")

        if notes:
            if len(notes) == 1:
                msg = "%s%s%s" % (msg, "\n Note that ", notes[0])
            else:
                msg += "\n Note that: "
                for cnt in range(len(notes)):
                    msg += '\n%s. %s' % (cnt + 1, notes[cnt])

        super(UnexpectedOutput, self).__init__(command, output=output,
                                               _subclass_msg=msg)


class UnknownCLIMode(CmdlineException):
    """
    Exception for any CLI that sees or is asked for an unknown mode.

    :param prompt: The prompt seen that cannot be mapped to a mode
    :param mode: The mode that was requested but not recognized

    :ivar prompt: The prompt seen that cannot be mapped to a mode
    :ivar mode: The mode that was requested but not recognized
    """

    def __init__(self, prompt=None, mode=None):
        self.prompt = prompt
        self.mode = mode

        if prompt is not None:
            if mode is not None:
                msg = ("Unknown mode '%s' seen or requested, prompt is '%s'" %
                       (mode, prompt))
            else:
                msg = "Unknown mode seen, prompt is '%s'" % prompt
        elif mode is not None:
            msg = "Unknown mode '%s' requested." % mode
        else:
            msg = "Unknown mode seen or requested, no details available."

        super(UnknownCLIMode, self).__init__(_subclass_msg=msg)
