import logging
import subprocess

import win32api
import win32service
import win32serviceutil

import peek_worker

logger = logging.getLogger(__name__)
from peek_platform.sw_install.PeekSwInstallManagerABC import IS_WIN_SVC


class PeekSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = "peek-worker"
    _svc_display_name_ = "Peek Worker " + peek_worker.__version__
    _exe_args_ = IS_WIN_SVC  # Not needed here

    # The worker doesn't start until the peek-server is up and running.
    # We might not be running on the same box as the redis, postgres, etc.
    _svc_deps_ = ["RpcSs"]

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)

        self._runningPid = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        if self._runningPid is None:
            return

        PROCESS_TERMINATE = 1
        handle = win32api.OpenProcess(
            PROCESS_TERMINATE, False, self._runningPid)
        win32api.TerminateProcess(handle, -1)
        win32api.CloseHandle(handle)

        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        try:

            proc = subprocess.Popen(
                ["run_peek_worker.exe", IS_WIN_SVC]
            )
            self._runningPid = proc.pid
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)

            proc.communicate()

        except Exception as e:
            logger.exception(e)
            raise


def main():
    win32serviceutil.HandleCommandLine(PeekSvc)


if __name__ == '__main__':
    main()
