# encoding: utf-8

import logging_helper
from uiutil import Position, Label
from uiutil.tk_names import W
from configurationutil.gui import ConfigSelectorFrame
from ... import config
from ...endpoints import Endpoints
from ..window import AddEditEndpointWindow

logging = logging_helper.setup_logging()


class EndpointConfigFrame(ConfigSelectorFrame):

    HEADINGS = [
        u'Endpoint',
        u'Path'
    ]

    ADD_EDIT_WINDOW_CLASS = AddEditEndpointWindow

    CONFIG_ROOT = config.ENDPOINT_CONFIG

    def __init__(self,
                 *args,
                 **kwargs):
        super(EndpointConfigFrame, self).__init__(items=Endpoints,
                                                  cfg=config.RegisterAPIConfig().endpoints,
                                                  *args,
                                                  **kwargs)

    def draw_additional_columns(self,
                                item):

        Label(frame=self._scroll_frame,
              text=self._items[item].path,
              row=Position.CURRENT,
              column=Position.NEXT,
              sticky=W)
