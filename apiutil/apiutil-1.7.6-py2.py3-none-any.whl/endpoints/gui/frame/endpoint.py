# encoding: utf-8

import json
import logging_helper
from uiutil import Position, Label, TextEntry
from uiutil.tk_names import E, EW
from configurationutil.gui import AddEditInheritableConfigFrame, ParamsConfigButton
from ..._constants import EndpointKeysConstant
from ... import config
from ...endpoints import Endpoints

logging = logging_helper.setup_logging()


class AddEditEndpointFrame(AddEditInheritableConfigFrame):

    CONFIG_ROOT = config.ENDPOINT_CONFIG

    def __init__(self,
                 *args,
                 **kwargs):
        super(AddEditEndpointFrame, self).__init__(cfg=config.RegisterAPIConfig().endpoints,
                                                   inheritable_items=sorted(Endpoints().keys()),
                                                   *args,
                                                   **kwargs)

    def draw_defaults(self):

        Label(text=u'Path:',
              row=Position.NEXT,
              column=Position.START,
              sticky=E)

        self._path = TextEntry(value=(self.defaults.get(EndpointKeysConstant.path, u'')
                                      if self.edit
                                      else u''),
                               row=Position.CURRENT,
                               column=Position.NEXT,
                               sticky=EW)

        Label(text=u'Parameters:',
              row=Position.NEXT,
              column=Position.START,
              sticky=E)

        self._params = ParamsConfigButton(frame=self,
                                          params=(self.defaults.get(EndpointKeysConstant.params)
                                                  if self.edit
                                                  else None),
                                          width=self.BUTTON_WIDTH,
                                          row=Position.CURRENT,
                                          column=Position.NEXT,
                                          sticky=EW)

    def save_defaults(self):

        default_vars = [
            (self._path, EndpointKeysConstant.path)
        ]

        defaults = {}

        for default in default_vars:
            value = default[0].value
            if value:
                defaults[default[1]] = value

        # Decode params
        if self._params.params:
            defaults[EndpointKeysConstant.params] = self._params.params

        return defaults
