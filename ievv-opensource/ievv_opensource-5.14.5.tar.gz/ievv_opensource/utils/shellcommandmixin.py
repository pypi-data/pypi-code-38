from __future__ import print_function
from __future__ import unicode_literals

import psutil
import sh


try:
    from shlex import quote as shell_quote
except ImportError:
    from pipes import quote as shell_quote


class ShellCommandError(Exception):
    """
    Raised when :meth:`.LogMixin.run_shell_command` fails.
    """


class ShellCommandMixin(object):
    """
    Shell command mixin - for classes that need to run shell commands.

    Requires :class:`~ievv_opensource.utils.logmixin.LogMixin`.
    """
    def log_shell_command_stdout(self, line):
        """
        Called by :meth:`.run_shell_command` each time the shell
        command outputs anything to stdout.
        """
        self.get_logger().stdout(line.rstrip())

    def log_shell_command_stderr(self, line):
        """
        Called by :meth:`.run_shell_command` each time the shell
        command outputs anything to stderr.
        """
        self.get_logger().stderr(line.rstrip())

    def prettyformat_shell_command(self, executable, args=None, kwargs=None, _cwd=None):
        output = [executable]
        if args:
            output.extend([shell_quote(arg) for arg in args])
        if kwargs:
            for key, value in kwargs.items():
                if value:
                    if len(key) == 1:
                        prefix = '-'
                    else:
                        prefix = '--'
                    if value is True:
                        formatted_value = ''
                    else:
                        formatted_value = '={}'.format(value)
                    output.append('{prefix}{key}{formatted_value}'.format(
                        prefix=prefix,
                        key=key,
                        formatted_value=formatted_value
                    ))
        if _cwd:
            output.insert(0, '[CWD={}]'.format(_cwd))

        return ' '.join(output)

    def run_shell_command(self, executable, args=None, kwargs=None, _cwd=None,
                          _out=None, _err=None, _env=None):
        """
        Run a shell command.

        Parameters:
            executable: The name or path of the executable.
            args: List of arguments for the ``sh.Command`` object.
            kwargs: Dict of keyword arguments for the ``sh.Command`` object.

        Raises:
            ShellCommandError: When the command fails. See :class:`.ShellCommandError`.
        """
        self.get_logger().debug('Execute: {}'.format(self.prettyformat_shell_command(
            executable=executable, args=args, kwargs=kwargs, _cwd=_cwd)))
        command = sh.Command(executable)
        args = args or []
        kwargs = kwargs or {}
        if _cwd:
            kwargs['_cwd'] = _cwd
        if _env:
            kwargs['_env'] = _env

        _out = _out or self.log_shell_command_stdout
        _err = _err or self.log_shell_command_stderr

        try:
            return command(*args,
                           _out=_out,
                           _err=_err,
                           **kwargs)
        except sh.ErrorReturnCode:
            # We do not need to show any more errors here - they
            # have already been printed by the _out and _err handlers.
            raise ShellCommandError()

    def kill_process(self, pid):
        """
        Kill the system process with the given ``pid``, and all
        its child processes.

        .. warning::

            You should normally use :meth:`.terminate_process` instead of
            this method since that normally gives the process the chance to
            cleanup.

        Parameters:
            pid: The process ID of the process you want to kill.

        Returns:
            A list of all the killed processes.
        """
        process_ids = []
        try:
            process = psutil.Process(pid)
        except psutil.NoSuchProcess:
            pass
        else:
            for childprocess in process.children():
                process_ids.append(childprocess.pid)
                childprocess.kill()
            process_ids.append(process.pid)
            process.kill()
        return process_ids

    def terminate_process(self, pid):
        """
        Terminate the system process with the given ``pid``, and all
        its child processes.

        Parameters:
            pid: The process ID of the process you want to terminate.

        Returns:
            A list of all the terminated processes.
        """
        process_ids = []
        try:
            process = psutil.Process(pid)
        except psutil.NoSuchProcess:
            pass
        else:
            for childprocess in process.children():
                process_ids.append(childprocess.pid)
                childprocess.terminate()
            try:
                process.terminate()
            except psutil.NoSuchProcess:
                pass
            else:
                process_ids.append(process.pid)
        return process_ids
