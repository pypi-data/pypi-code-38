# encoding: utf-8

import logging_helper
from uiutil.tk_names import EW
from uiutil.helper.layout import nice_grid
from uiutil import RootWindow, ChildWindow
from uiutil.mixin.menubar import OptionTypes
from classutils.decorators import profiling
from ...dns_server import DNSServer
from ..frame.server import DNSServerFrame

logging = logging_helper.setup_logging()


class _DNSServerWindow(object):

    def __init__(self,
                 server=DNSServer,
                 server_kwargs=None,
                 zone_address_list=None,
                 *args,
                 **kwargs):

        self.server = server
        self.server_kwargs = server_kwargs
        self.zone_address_list = zone_address_list

        super(_DNSServerWindow, self).__init__(*args,
                                               **kwargs)

    def _draw_widgets(self):
        self.title(u"DNS Server")

        self.server = DNSServerFrame(server=self.server,
                                     server_kwargs=self.server_kwargs,
                                     zone_address_list=self.zone_address_list,
                                     sticky=EW)

        nice_grid(self.server)


class DNSServerRootWindow(_DNSServerWindow, RootWindow):
    DEBUG_MENU_ENABLED = True


class DNSServerChildWindow(_DNSServerWindow, ChildWindow):
    pass
