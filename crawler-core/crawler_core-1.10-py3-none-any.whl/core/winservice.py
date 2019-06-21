# requires pywin32
import socket
import traceback
import win32event
import win32service
import servicemanager
import win32serviceutil


class WinService(win32serviceutil.ServiceFramework):

    _svc_name_ = 'PyhonService'
    _svc_display_name_ = 'Pyhon Service'
    _svc_description_ = 'Python Service Description'

    @classmethod
    def parse_command_line(cls):
        """This method is parsing command lines"""
        win32serviceutil.HandleCommandLine(cls)

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        """This method stops service when asked"""
        self.stop()
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        """This method that calls for start service and loggger"""
        self.start()
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        try:
            self.main()
        except:
            servicemanager.LogErrorMsg(traceback.format_exc())  # if error print it to event

    def start(self):
        """Method that starts service and where we can
        add some conditions that must be in to run service."""
        pass

    def stop(self):
        """Method that stops service and where we can
        add some conditions that must be in to run service."""
        pass

    def main(self):
        """Method that will run inside service."""
        pass


# if __name__ == '__main__':
#     WinService.parse_command_line()