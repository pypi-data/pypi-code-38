import platform


try:
    import win32serviceutil
    import win32service
    import win32event
    import win32api
except ImportError as e:
    if platform.system() is "Windows":
        raise

from twisted.internet import reactor
import time

import peek_platform
import logging
logger = logging.getLogger(__name__)


class PeekSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = "peek-restarter"
    _svc_display_name_ = "Peek Restarter " + peek_platform.__version__
    _svc_deps_ = ["RpcSs"]

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        try:
            from peek_platform.util.LogUtil import setupPeekLogger
            setupPeekLogger(self._svc_name_)

            while True:
                retval = win32event.WaitForSingleObject(self.hWaitStop, 2000)
                if retval != win32event.WAIT_TIMEOUT:
                    break

                for service in ("peek-agent", "peek-worker", "peek-client"):
                    (_, status, _, errCode, _, _, _) = (
                        win32serviceutil.QueryServiceStatus(service)
                    )

                    if status != win32service.SERVICE_STOPPED:
                        continue

                    logger.info("Starting service %s", service)
                    win32serviceutil.StartService(service)
                    win32serviceutil.WaitForServiceStatus(
                        service,
                        win32service.SERVICE_RUNNING,
                        waitSecs=600
                    )
                    logger.info("Service %s started", service)

        except Exception as e:
            logger.exception(e)

        self.ReportServiceStatus(win32service.SERVICE_STOPPED)


def main():
    win32serviceutil.HandleCommandLine(PeekSvc)


if __name__ == '__main__':
    main()
