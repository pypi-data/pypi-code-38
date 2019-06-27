import os
import signal
import subprocess
from datetime import datetime
from logging import Logger
from typing import List

from sidecar.app_instance_identifier import IIdentifier
from sidecar.health_check.health_check_executor_logger import HealthCheckExecutorLogger
from sidecar.model.objects import SidecarApplication
from sidecar.non_blocking_stream_reader import NonBlockingStreamReader
from sidecar.utils import CallsLogger


class HealthCheckExecutor:

    def __init__(self,
                 apps: List[SidecarApplication],
                 executor_logger: HealthCheckExecutorLogger,
                 logger: Logger):
        self._apps = apps
        self._executor_logger = executor_logger
        self._logger = logger

    @CallsLogger.wrap
    def start(self, identifier: IIdentifier, cmd: List[str]) -> bool:

        app = next(iter([app for app in self._apps if app.name == identifier.name]), None)  # type: SidecarApplication

        self._executor_logger.log_start(identifier=identifier, cmd=cmd, timeout=app.healthcheck_timeout)
        env = {**os.environ, **app.env}

        start = datetime.now()
        timed_out = False
        read_interval = 0.5
        
        """
        run healthcheck command in subprocess and redirect its outputs to subprocess' stdout
        read stdout line by line until subprocess ended or until timeout and send it to cloud logger
        if timeout occurred kill healthcheck subprocess
        """
        with subprocess.Popen(cmd,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              shell=True,
                              preexec_fn=os.setsid,
                              universal_newlines=True,
                              env=env) as p:
            try:
                stdout_stream_reader = NonBlockingStreamReader(stream=p.stdout, interval=read_interval)
                stderr_stream_reader = NonBlockingStreamReader(stream=p.stderr, interval=read_interval)
                self._logger.info('running command {0}'.format(cmd))

                while True:
                    line = stdout_stream_reader.read_line(read_interval)
                    if line:
                        self._executor_logger.log_line(line, identifier)

                    line = stderr_stream_reader.read_line(read_interval)
                    if line:
                        self._executor_logger.log_line(line, identifier, True)

                    elapsed = datetime.now() - start

                    if elapsed.total_seconds() > app.healthcheck_timeout:
                        stdout_stream_reader.stop()
                        stderr_stream_reader.stop()
                        raise subprocess.TimeoutExpired(cmd=cmd, timeout=app.healthcheck_timeout)

                    if p.poll() is not None:
                        while True:
                            line = stdout_stream_reader.read_line(read_interval)
                            if line:
                                self._executor_logger.log_line(line, identifier)
                            else:
                                stdout_stream_reader.stop()
                                break

                        while True:
                            line = stderr_stream_reader.read_line(read_interval)
                            if line:
                                self._executor_logger.log_line(line, identifier, True)
                            else:
                                stderr_stream_reader.stop()
                                break
                        break
            except subprocess.TimeoutExpired as ex:
                self._executor_logger.log_timeout(timeout=ex.timeout, identifier=identifier)
                self._kill_process(process=p)
                timed_out = True
            finally:
                if timed_out:
                    return False
                process_exit_code = p.returncode
                if process_exit_code == 0:
                    self._executor_logger.log_success(identifier=identifier)
                    return True
                else:
                    self._executor_logger.log_error(identifier=identifier, exit_code=process_exit_code)
                    return False

    def _kill_process(self, process):
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        except ProcessLookupError as ex:
            self._logger.exception('Could not kill process, pid {} due to {}'.format(
                process.pid,
                str(ex)))
