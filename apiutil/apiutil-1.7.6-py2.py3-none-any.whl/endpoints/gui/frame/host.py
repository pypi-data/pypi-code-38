# encoding: utf-8

import logging_helper
from uiutil import Position, Label, TextEntry, IntEntry
from uiutil.tk_names import E, EW
from configurationutil.gui import AddEditInheritableConfigFrame
from ..._constants import HostKeysConstant
from ... import config
from ...hosts import Hosts

logging = logging_helper.setup_logging()


class AddEditHostFrame(AddEditInheritableConfigFrame):

    CONFIG_ROOT = config.HOST_CONFIG

    def __init__(self,
                 *args,
                 **kwargs):
        super(AddEditHostFrame, self).__init__(cfg=config.RegisterAPIConfig().hosts,
                                               inheritable_items=sorted(Hosts().keys()),
                                               *args,
                                               **kwargs)

    def draw_defaults(self):

        Label(text=u'Protocol:',
              row=Position.NEXT,
              column=Position.START,
              sticky=E)

        self._protocol = TextEntry(value=self.defaults.get(HostKeysConstant.protocol, u'http')
                                   if self.edit else u'http',
                                   row=Position.CURRENT,
                                   column=Position.NEXT,
                                   sticky=EW)

        Label(text=u'Domain:',
              row=Position.NEXT,
              column=Position.START,
              sticky=E)

        self._domain = TextEntry(value=self.defaults.get(HostKeysConstant.domain, u'')
                                 if self.edit else u'',
                                 row=Position.CURRENT,
                                 column=Position.NEXT,
                                 sticky=EW)

        Label(text=u'Port:',
              row=Position.NEXT,
              column=Position.START,
              sticky=E)

        self._port = IntEntry(value=self.defaults.get(HostKeysConstant.port, 80)
                              if self.edit else 80,
                              row=Position.CURRENT,
                              column=Position.NEXT,
                              sticky=EW)

        Label(text=u'Secret / Key:',
              row=Position.NEXT,
              column=Position.START,
              sticky=E)

        self._secret_key = TextEntry(value=self.defaults.get(HostKeysConstant.secret_key, u'')
                                     if self.edit else u'',
                                     row=Position.CURRENT,
                                     column=Position.NEXT,
                                     sticky=EW)

        Label(text=u'Username:',
              row=Position.NEXT,
              column=Position.START,
              sticky=E)

        self._username = TextEntry(value=self.defaults.get(HostKeysConstant.user, u'')
                                   if self.edit else u'',
                                   row=Position.CURRENT,
                                   column=Position.NEXT,
                                   sticky=EW)

        Label(text=u'Password:',
              row=Position.NEXT,
              column=Position.START,
              sticky=E)

        self._password = TextEntry(value=self.defaults.get(HostKeysConstant.password, u'')
                                   if self.edit else u'',
                                   row=Position.CURRENT,
                                   column=Position.NEXT,
                                   sticky=EW)

    def save_defaults(self):

        default_vars = [
            (self._protocol, HostKeysConstant.protocol),
            (self._domain, HostKeysConstant.domain),
            (self._port, HostKeysConstant.port),
            (self._secret_key, HostKeysConstant.secret_key),
            (self._username, HostKeysConstant.user),
            (self._password, HostKeysConstant.password)
        ]

        defaults = {}

        for default in default_vars:
            value = default[0].value
            if value:
                defaults[default[1]] = value

        return defaults
