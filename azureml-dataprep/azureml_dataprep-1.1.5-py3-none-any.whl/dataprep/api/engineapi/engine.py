# Copyright (c) Microsoft Corporation. All rights reserved.
"""Launch and exchange messages with the engine."""
import atexit
import json
import os
import subprocess
import sys
from enum import Enum
from uuid import UUID, uuid1

from dotnetcore2 import runtime
from ..errorhandlers import raise_engine_error

from .._loggerfactory import session_id, instrumentation_key

class CustomEncoder(json.JSONEncoder):
    """Custom Encoding"""
    # pylint: disable=E0202
    def default(self, o):
        if isinstance(o, UUID):
            return str(o)
        if isinstance(o, Enum):
            return o.value
        if hasattr(o, 'to_pod'):
            return o.to_pod()
        if hasattr(o, '__dict__'):
            return {CustomEncoder._to_camel_case(k): v for k, v in vars(o).items()}
        return json.JSONEncoder.default(self, o)

    @staticmethod
    def _to_camel_case(value: str) -> str:
        first, *others = value.lstrip('_').split('_')
        return ''.join([first.lower(), *map(str.title, others)])


class MessageChannel:
    """Channel for JSON messages to the local engine process."""
    def __init__(self, process: subprocess.Popen):
        self._process = process
        self._last_message_id = 0

    def close(self):
        """Close the underlying process."""
        self._process.terminate()
        try:
            self._process.wait(10)
        except subprocess.TimeoutExpired:
            self._process.kill()

    def send_message(self, op_code: str, message: object) -> object:
        """Send a message to the engine, and wait for its response."""
        self._last_message_id += 1
        message_id = self._last_message_id
        self._write_line(json.dumps({
            "messageId": message_id,
            "opCode": op_code,
            "data": message
        }, cls=CustomEncoder))

        while True:
            response = self._read_response()
            if 'error' in response:
                raise_engine_error(response['error'])
            elif response.get('id') == message_id:
                return response['result']

    def _write_line(self, line: str):
        self._raise_error_if_process_terminated()
        self._process.stdin.write(line.encode())
        self._process.stdin.write('\n'.encode())
        self._process.stdin.flush()

    def _read_response(self) -> dict:
        self._raise_error_if_process_terminated()
        string = None
        while string is None:
            line = self._process.stdout.readline()
            string = line.decode()
            if len(string) == 0 or string[0] != '{':
                string = None

        parsed = None
        try:
            parsed = json.loads(string)
        finally:
            if parsed is None:  # Exception is being thrown
                print("Line read from engine could not be parsed as JSON. Line:")
                try:
                    print(string)
                except UnicodeEncodeError:
                    print(bytes(string, 'utf-8'))
        return parsed

    def _raise_error_if_process_terminated(self):
        if self._process.poll() is not None:
            raise ChildProcessError('Engine process exited unexpectedly.')


def launch_engine() -> MessageChannel:
    """Launch the engine process and set up a MessageChannel."""
    engine_args = {
        'debug': 'false',
        'firstLaunch': 'false',
        'sessionId': session_id,
        'invokingPythonPath': sys.executable,
        'invokingPythonWorkingDirectory': os.path.join(os.getcwd(), ''),
        'instrumentationKey': '' if os.environ.get('DISABLE_DPREP_LOGGER') is not None else instrumentation_key
    }

    engine_path = _get_engine_path()
    dependencies_path = runtime.ensure_dependencies()
    dotnet_path = runtime.get_runtime_path()
    env = os.environ.copy()
    env['DOTNET_SYSTEM_GLOBALIZATION_INVARIANT'] = 'true'
    if dependencies_path is not None:
        env['LD_LIBRARY_PATH'] = dependencies_path
    _set_sslcert_path(env)

    process = subprocess.Popen(
        [dotnet_path, engine_path, json.dumps(engine_args)],
        bufsize=5 * 1024 * 1024,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,  # Hide spurious dotnet errors (Vienna:45714) TODO: collect Errors
        env=env)
    channel = MessageChannel(process)
    atexit.register(channel.close)
    return channel


def _get_engine_path():
    engine_dll = "Microsoft.DPrep.Execution.EngineHost.dll"
    current_folder = os.path.dirname(os.path.realpath(__file__))
    engine_path = os.path.join(current_folder, 'bin', engine_dll)
    return engine_path


def _set_sslcert_path(env):
    if sys.platform in ['win32', 'darwin']:
        return  # no need to set ssl cert path for Windows and macOS

    SSL_CERT_FILE = 'SSL_CERT_FILE'
    if SSL_CERT_FILE in env:
        return # skip if user has set SSL_CERT_FILE

    try:
        import certifi
        cert_path = os.path.join(os.path.dirname(certifi.__file__), 'cacert.pem')
        if os.path.isfile(cert_path):
            env[SSL_CERT_FILE] = cert_path
    except Exception:
        pass # keep going since the trusted cert is only missing for some distro of Linux
