# encoding: utf-8

import logging_helper
from future.utils import iteritems
from uiutil import Position, Label, SwitchBox, Switch, Combobox
from uiutil.tk_names import N, E, EW, NORMAL
from configurationutil.gui import AddEditInheritableConfigFrame, ParamsConfigButton
from ..._constants import APIKeysConstant
from ... import config
from ... import APIS, Endpoints, Hosts

logging = logging_helper.setup_logging()


class AddEditAPIFrame(AddEditInheritableConfigFrame):

    CONFIG_ROOT = config.API_CONFIG

    def __init__(self,
                 *args,
                 **kwargs):
        super(AddEditAPIFrame, self).__init__(cfg=config.RegisterAPIConfig().apis,
                                              inheritable_items=sorted(APIS().keys()),
                                              *args,
                                              **kwargs)

    def draw_defaults(self):

        Label(text=u'API Family:',
              row=Position.NEXT,
              column=Position.START,
              sticky=E)

        self._family = Combobox(value=self.defaults.get(APIKeysConstant.family, u'')
                                if self.edit else u'',
                                values=[u''] + list(set(api.family for _, api in iteritems(APIS()))),
                                state=NORMAL,
                                row=Position.CURRENT,
                                column=Position.NEXT,
                                sticky=EW)

        Label(text=u'Host:',
              row=Position.NEXT,
              column=Position.START,
              sticky=E)

        self._host = Combobox(value=self.defaults.get(APIKeysConstant.host, u'')
                              if self.edit else u'',
                              values=[u''] + [host for host in Hosts()],
                              row=Position.CURRENT,
                              column=Position.NEXT,
                              sticky=EW)

        Label(text=u'Endpoints:',
              row=Position.NEXT,
              column=Position.START,
              sticky=(N, E))

        endpoints = Endpoints()
        api_endpoints = self.defaults.get(APIKeysConstant.endpoints, []) if self.edit else []

        self._endpoints = SwitchBox(switches=[endpoint for endpoint in endpoints],
                                    switch_states={ep: Switch.ON if ep in api_endpoints else Switch.OFF
                                                   for ep in endpoints},
                                    height=100,
                                    sort=True,
                                    scroll=True,
                                    row=Position.CURRENT,
                                    column=Position.NEXT,
                                    sticky=EW)

        Label(text=u'Parameters:',
              row=Position.NEXT,
              column=Position.START,
              sticky=E)

        self._params = ParamsConfigButton(frame=self,
                                          params=self.defaults.get(APIKeysConstant.params) if self.edit else None,
                                          width=self.BUTTON_WIDTH,
                                          row=Position.CURRENT,
                                          column=Position.NEXT,
                                          sticky=EW)

    def save_defaults(self):

        default_vars = [
            (self._family, APIKeysConstant.family),
            (self._host, APIKeysConstant.host)
        ]

        defaults = {}

        for default in default_vars:
            value = default[0].value
            if value:
                defaults[default[1]] = value

        # Decode endpoints
        defaults[APIKeysConstant.endpoints] = [sw
                                               for sw, sw_state in iteritems(self._endpoints.all_states)
                                               if sw_state == Switch.ON]

        # Decode params
        if self._params.params:
            defaults[APIKeysConstant.params] = self._params.params

        return defaults
