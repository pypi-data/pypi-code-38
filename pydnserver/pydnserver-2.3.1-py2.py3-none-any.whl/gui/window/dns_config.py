# encoding: utf-8

from uiutil.window.root import RootWindow
from uiutil.window.child import ChildWindow
from ..frame.dns_config import DNSConfigFrame


class _DNSConfigWindow(object):

    def __init__(self,
                 zone_address_list=None,
                 *args,
                 **kwargs):

        self.zone_address_list = zone_address_list

        super(_DNSConfigWindow, self).__init__(*args,
                                               **kwargs)

    def _draw_widgets(self):
        self.title(u'DNS Config')
        self.dynamic_frame = DNSConfigFrame(parent=self._main_frame,
                                            zone_address_list=self.zone_address_list)


class DNSConfigRootWindow(_DNSConfigWindow, RootWindow):

    def __init__(self,
                 *args,
                 **kwargs):
        super(DNSConfigRootWindow, self).__init__(*args,
                                                  **kwargs)


class DNSConfigChildWindow(_DNSConfigWindow, ChildWindow):

    def __init__(self,
                 *args,
                 **kwargs):
        super(DNSConfigChildWindow, self).__init__(*args,
                                                   **kwargs)
