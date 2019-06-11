# encoding: utf-8

import logging_helper
from uiutil import Position, Label
from uiutil.tk_names import W
from configurationutil.gui import ConfigSelectorFrame
from ... import config
from ... import Environments
from ..window import AddEditEnvironmentWindow

logging = logging_helper.setup_logging()


class EnvironmentConfigFrame(ConfigSelectorFrame):

    HEADINGS = [
        u'Environment',
        u'Location'
    ]

    ADD_EDIT_WINDOW_CLASS = AddEditEnvironmentWindow

    CONFIG_ROOT = config.ENVIRONMENT_CONFIG

    def __init__(self,
                 *args,
                 **kwargs):
        super(EnvironmentConfigFrame, self).__init__(items=Environments,
                                                     cfg=config.RegisterAPIConfig().environments,
                                                     *args,
                                                     **kwargs)

    def draw_additional_columns(self,
                                item):

        try:
            location = self._items[item].location

        except AttributeError:
            location = u''

        Label(frame=self._scroll_frame,
              text=location,
              row=Position.CURRENT,
              column=Position.NEXT,
              sticky=W)
