import os
import subprocess

from tcell_agent.agent import TCellAgent
from tcell_agent.global_state import django_active, flask_active
from tcell_agent.policies.policy_types import PolicyTypes
from tcell_agent.instrumentation.decorators import catches_generic_exception
from tcell_agent.instrumentation.manager import InstrumentationManager
from tcell_agent.utils.compat import a_string


def get_tcell_context():
    if django_active():
        from tcell_agent.instrumentation.djangoinst.middleware.globalrequestmiddleware import GlobalRequestMiddleware
        request = GlobalRequestMiddleware.get_current_request()
        if request and request._tcell_context:
            return request._tcell_context

    elif flask_active():
        from flask.globals import _request_ctx_stack
        if _request_ctx_stack.top and _request_ctx_stack.top.request:
            return _request_ctx_stack.top.request._tcell_context

    return None


@catches_generic_exception(__name__,
                           "Error in command injection inspection",
                           return_value=False)
def should_block_shell_command(command):
    if command is None:
        return False

    if not a_string(command):
        command = " ".join(command)

    tcell_context = get_tcell_context()
    command_injection_policy = TCellAgent.get_policy(PolicyTypes.COMMAND_INJECTION)
    return command_injection_policy.block_command(command, tcell_context)


def instrument_os_system():
    class TCellDefaultFlag(object):
        pass

    def _tcell_os_system(_tcell_original_system, cmd):
        if should_block_shell_command(cmd):
            return 1

        return _tcell_original_system(cmd)
    InstrumentationManager.instrument(os, "system", _tcell_os_system)

    def _tcell_os_popen(_tcell_original_popen, command, mode="r", bufsize=TCellDefaultFlag):
        if should_block_shell_command(command):
            from tempfile import TemporaryFile
            result = TemporaryFile(mode)
            return result

        if bufsize is TCellDefaultFlag:
            return _tcell_original_popen(command, mode)

        return _tcell_original_popen(command, mode, bufsize)
    InstrumentationManager.instrument(os, "popen", _tcell_os_popen)

    def _tcell_os_popen_two(_tcell_original_popen_two, cmd, mode="t", bufsize=TCellDefaultFlag):
        if should_block_shell_command(cmd):
            from tempfile import TemporaryFile
            writeable = TemporaryFile("w")
            output = TemporaryFile("r")
            return (writeable, output)

        if bufsize is TCellDefaultFlag:
            return _tcell_original_popen_two(cmd, mode)

        return _tcell_original_popen_two(cmd, mode, bufsize)

    if hasattr(os, "popen2"):
        InstrumentationManager.instrument(os, "popen2", _tcell_os_popen_two)

    def _tcell_os_popen_three(_tcell_original_popen_three, cmd, mode="t", bufsize=TCellDefaultFlag):
        if should_block_shell_command(cmd):
            from tempfile import TemporaryFile
            writeable = TemporaryFile("w")
            readable = TemporaryFile("r")
            error = TemporaryFile("r")
            return (writeable, readable, error)
        if bufsize is TCellDefaultFlag:
            return _tcell_original_popen_three(cmd, mode)

        return _tcell_original_popen_three(cmd, mode, bufsize)
    if hasattr(os, "popen3"):
        InstrumentationManager.instrument(os, "popen3", _tcell_os_popen_three)

    def _tcell_os_popen_four(_tcell_original_popen_four, cmd, mode="t", bufsize=TCellDefaultFlag):
        if should_block_shell_command(cmd):
            from tempfile import TemporaryFile
            writeable = TemporaryFile("w")
            output_n_error = TemporaryFile("r")
            return (writeable, output_n_error)
        if bufsize is TCellDefaultFlag:
            return _tcell_original_popen_four(cmd, mode)

        return _tcell_original_popen_four(cmd, mode, bufsize)
    if hasattr(os, "popen4"):
        InstrumentationManager.instrument(os, "popen4", _tcell_os_popen_four)

    def _tcell_subprocess_call(
            _tcell_original_subprocess_call,
            args,
            bufsize=0,
            executable=None,
            stdin=None,
            stdout=None,
            stderr=None,
            preexec_fn=None,
            close_fds=False,
            shell=False,
            cwd=None,
            env=None,
            universal_newlines=False,
            startupinfo=None,
            creationflags=0):
        if should_block_shell_command(args):
            return 1

        return _tcell_original_subprocess_call(
            args,
            bufsize=bufsize,
            executable=executable,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            preexec_fn=preexec_fn,
            close_fds=close_fds,
            shell=shell,
            cwd=cwd,
            env=env,
            universal_newlines=universal_newlines,
            startupinfo=startupinfo,
            creationflags=creationflags)
    InstrumentationManager.instrument(subprocess, "call", _tcell_subprocess_call)

    def _tcell_subprocess_check_output(
            _tcell_original_subprocess_check_output,
            args,
            bufsize=0,
            executable=None,
            stdin=None,
            stderr=None,
            preexec_fn=None,
            close_fds=False,
            shell=False,
            cwd=None,
            env=None,
            universal_newlines=False,
            startupinfo=None,
            creationflags=0):
        if should_block_shell_command(args):
            raise subprocess.CalledProcessError(1, args, b"Blocked by TCell")

        return _tcell_original_subprocess_check_output(
            args,
            bufsize=bufsize,
            executable=executable,
            stdin=stdin,
            stderr=stderr,
            preexec_fn=preexec_fn,
            close_fds=close_fds,
            shell=shell,
            cwd=cwd,
            env=env,
            universal_newlines=universal_newlines,
            startupinfo=startupinfo,
            creationflags=creationflags)
    InstrumentationManager.instrument(subprocess, "check_output", _tcell_subprocess_check_output)

    try:
        import popen2

        def _tcell_popen2_popen_two(_tcell_original_popen_two, cmd, bufsize=TCellDefaultFlag, mode="t"):
            if should_block_shell_command(cmd):
                from tempfile import TemporaryFile
                writeable = TemporaryFile("w")
                output = TemporaryFile("r")
                return (writeable, output)

            if bufsize is TCellDefaultFlag:
                return _tcell_original_popen_two(cmd, mode=mode)

            return _tcell_original_popen_two(cmd, bufsize, mode)
        InstrumentationManager.instrument(popen2, "popen2", _tcell_popen2_popen_two)

        def _tcell_popen2_popen_three(_tcell_original_popen_three, cmd, bufsize=TCellDefaultFlag, mode="t"):
            if should_block_shell_command(cmd):
                from tempfile import TemporaryFile
                writeable = TemporaryFile("w")
                readable = TemporaryFile("r")
                error = TemporaryFile("r")
                return (writeable, readable, error)

            if bufsize is TCellDefaultFlag:
                return _tcell_original_popen_three(cmd, mode=mode)

            return _tcell_original_popen_three(cmd, bufsize, mode)
        InstrumentationManager.instrument(popen2, "popen3", _tcell_popen2_popen_three)

        def _tcell_popen2_popen_four(_tcell_original_popen_four, cmd, bufsize=TCellDefaultFlag, mode="t"):
            if should_block_shell_command(cmd):
                from tempfile import TemporaryFile
                writeable = TemporaryFile("w")
                output_n_error = TemporaryFile("r")
                return (writeable, output_n_error)

            if bufsize is TCellDefaultFlag:
                return _tcell_original_popen_four(cmd, mode=mode)

            return _tcell_original_popen_four(cmd, bufsize, mode)
        InstrumentationManager.instrument(popen2, "popen4", _tcell_popen2_popen_four)

    except ImportError:
        pass


@catches_generic_exception(__name__, "Could not instrument for cmdi")
def instrument_commands():
    instrument_os_system()
