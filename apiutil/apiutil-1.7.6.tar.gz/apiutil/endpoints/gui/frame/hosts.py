# encoding: utf-8

import logging_helper
from uiutil import Position, Label
from uiutil.tk_names import W
from configurationutil.gui import ConfigSelectorFrame
from ... import config
from ...hosts import Hosts
from ..window import AddEditHostWindow

logging = logging_helper.setup_logging()


class HostConfigFrame(ConfigSelectorFrame):

    HEADINGS = [
        u'Host',
        u'Domain',
        u'Port'
    ]

    ADD_EDIT_WINDOW_CLASS = AddEditHostWindow

    CONFIG_ROOT = config.HOST_CONFIG

    def __init__(self,
                 *args,
                 **kwargs):
        super(HostConfigFrame, self).__init__(items=Hosts,
                                              cfg=config.RegisterAPIConfig().hosts,
                                              *args,
                                              **kwargs)

    def draw_additional_columns(self,
                                item):

        host = self._items[item]

        Label(frame=self._scroll_frame,
              text=host.domain,
              row=Position.CURRENT,
              column=Position.NEXT,
              sticky=W)

        Label(frame=self._scroll_frame,
              text=host.port,
              row=Position.CURRENT,
              column=Position.NEXT,
              sticky=W)
