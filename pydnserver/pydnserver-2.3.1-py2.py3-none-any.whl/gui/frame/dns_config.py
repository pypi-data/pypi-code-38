# encoding: utf-8

import logging_helper
from uiutil.tk_names import EW, HORIZONTAL
from uiutil import BaseLabelFrame, Button
from ..window.forwarders import ForwarderConfigWindow
from ..window.zone import ZoneConfigWindow

logging = logging_helper.setup_logging()


class DNSConfigFrame(BaseLabelFrame):

    BUTTON_WIDTH = 12

    def __init__(self,
                 title=u'DNS Config:',
                 zone_address_list=None,
                 *args,
                 **kwargs):

        self.zone_address_list = zone_address_list

        super(DNSConfigFrame, self).__init__(title=title,
                                             layout=HORIZONTAL,
                                             *args,
                                             **kwargs)

        Button(text=u"Forwarders",
               width=self.BUTTON_WIDTH,
               sticky=EW,
               command=self.launch_forwarder_config)

        Button(text=u"Zone",
               width=self.BUTTON_WIDTH,
               sticky=EW,
               command=self.launch_zone_config)

        self.nice_grid()

    def launch_forwarder_config(self):
        ForwarderConfigWindow(fixed=True,
                              parent_geometry=self.parent.winfo_toplevel().winfo_geometry())

    def launch_zone_config(self):
        ZoneConfigWindow(fixed=True,
                         parent_geometry=self.parent.winfo_toplevel().winfo_geometry(),
                         address_list=self.zone_address_list)
