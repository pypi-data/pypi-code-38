# encoding: utf-8

import logging_helper
from uiutil import Position, BaseFrame, Button, Separator
from uiutil.tk_names import NORMAL, EW, showerror, HORIZONTAL
from ...dns_server import DNSServer
from ..frame.dns_config import DNSConfigFrame
from ..._constants import (START_SERVERS,
                           STOP_SERVERS)

logging = logging_helper.setup_logging()


class DNSServerFrame(BaseFrame):
    BUTTON_WIDTH = 20

    def __init__(self,
                 server=DNSServer,
                 server_kwargs=None,
                 zone_address_list=None,
                 *args,
                 **kwargs):

        BaseFrame.__init__(self,
                           layout=HORIZONTAL,
                           *args,
                           **kwargs)

        if server_kwargs is None:
            server_kwargs = {}

        self.server = server(**server_kwargs)

        self.dns_config = DNSConfigFrame(row=Position.NEXT,
                                         sticky=EW,
                                         zone_address_list=zone_address_list)

        Separator()

        self.start_stop_button = Button(state=NORMAL,
                                        value=START_SERVERS,
                                        width=self.BUTTON_WIDTH,
                                        command=self.start_stop,
                                        row=Position.NEXT,
                                        sticky=EW,
                                        tooltip=u'')

    def start_stop(self):
        if self.start_stop_button.value == START_SERVERS:
            self.start()
        else:
            self.stop()

    def start(self):

        try:
            self.server.start()
            self.start_stop_button.value = STOP_SERVERS

        except Exception as err:
            logging.exception(err)
            logging.fatal(u'Unexpected Exception.')

            showerror(title=u'Server startup failed!',
                      message=u'Failed to start DNS Server: {err}'.format(err=err))

            self.stop()

    def stop(self):
        self.server.stop()
        self.start_stop_button.value = START_SERVERS
