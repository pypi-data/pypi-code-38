# encoding: utf-8

import logging_helper
from uiutil import Position, Label
from uiutil.tk_names import W
from configurationutil.gui import ConfigSelectorFrame
from ... import config
from ...apis import APIS
from ..window import AddEditAPIWindow

logging = logging_helper.setup_logging()


class APIConfigFrame(ConfigSelectorFrame):

    HEADINGS = [
        u'API',
        u'Family',
        u'Host'
    ]

    ADD_EDIT_WINDOW_CLASS = AddEditAPIWindow

    CONFIG_ROOT = config.API_CONFIG

    def __init__(self,
                 *args,
                 **kwargs):
        super(APIConfigFrame, self).__init__(items=APIS,
                                             cfg=config.RegisterAPIConfig().apis,
                                             *args,
                                             **kwargs)

    def draw_additional_columns(self,
                                item):

        api = self._items[item]

        Label(frame=self._scroll_frame,
              text=api.family,
              row=Position.CURRENT,
              column=Position.NEXT,
              sticky=W)

        Label(frame=self._scroll_frame,
              text=api.host.key,
              row=Position.CURRENT,
              column=Position.NEXT,
              sticky=W)
