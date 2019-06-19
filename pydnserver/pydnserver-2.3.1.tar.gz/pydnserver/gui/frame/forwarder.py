# encoding: utf-8

import logging_helper
from uiutil.tk_names import HORIZONTAL, E, EW, NORMAL, DISABLED
from tkinter.messagebox import showerror
from tableutil import Table
from collections import OrderedDict
from uiutil import BaseFrame, Label, Button, TextEntry, Separator, Position, Spacer
from configurationutil import Configuration
from networkutil.gui.ipv4_widget import IPv4NetworkEntry
from networkutil.validation import valid_ipv4
from fdutil.string_tools import make_multi_line_list
from ipaddress import IPv4Network, IPv4Address
from ...config import dns_forwarders

logging = logging_helper.setup_logging()


class AddEditForwarderFrame(BaseFrame):

    DEFAULT_NETWORK = u'0.0.0.0'
    DEFAULT_FORWARDERS = u'8.8.8.8, 8.8.4.4'

    BUTTON_WIDTH = 15

    def __init__(self,
                 selected_record=None,
                 edit=False,
                 *args,
                 **kwargs):

        BaseFrame.__init__(self,
                           layout=HORIZONTAL,
                           *args,
                           **kwargs)

        self.edit = edit

        self.cfg = Configuration()

        if selected_record:
            key = u'{cfg}.{int}'.format(cfg=dns_forwarders.DNS_SERVERS_CFG,
                                        int=selected_record)
            self.selected_record = {
                u'interface': selected_record,
                u'forwarders': self.cfg[key]
            }

        else:
            self.selected_record = None

        self._draw()

    def _draw(self):

        Label(text=u'Network:',
              sticky=E,
              tooltip=self.tooltip)

        self._network = IPv4NetworkEntry(value=(self.selected_record[u'interface'] if self.edit else u''),
                                         state=DISABLED if self.edit else NORMAL,
                                         strict=False,
                                         sticky=EW,
                                         columnspan=3,
                                         tooltip=Table.init_from_tree([u'The following are all the same:',
                                                                       u' - 192.168.1.0 (assumes /24)',
                                                                       u' - 192.168.1.0/24.',
                                                                       u' - 192.168.1.0/255.255.255.0',
                                                                       u' - 192.168.1.0/0.0.0.255',
                                                                       u' - Also accepts any ip from the network',
                                                                       u'   (192.168.1.10/24) and will convert this',
                                                                       u'   to the network address (192.168.1.0/24)'],
                                                                      title=u'IP network',
                                                                      table_format=Table.LIGHT_TABLE_FORMAT).text())

        Label(text=u'Forwarders:',
              row=Position.NEXT,
              sticky=E,
              tooltip=self.tooltip)

        self._forwarders = TextEntry(value=(u', '.join(self.selected_record[u'forwarders'])
                                            if self.edit
                                            else self.DEFAULT_FORWARDERS),
                                     sticky=EW,
                                     columnspan=3,
                                     tooltip=u'comma separated list of nameserver addresses')

        Separator()

        Spacer()

        Button(text=u'Cancel',
               command=self._cancel,
               width=self.BUTTON_WIDTH,
               sticky=EW)

        Button(text=u'Save',
               command=self._save,
               width=self.BUTTON_WIDTH,
               sticky=EW)

        self.nice_grid()

    def _save(self):

        try:
            network = self._network.value
            network = IPv4Network(u'{ip}{prefix_len}'.format(ip=network,
                                                             prefix_len=u'' if u'/' in network else u'/24'),
                                  strict=False)

            key = u'{cfg}.{int}'.format(cfg=dns_forwarders.DNS_SERVERS_CFG,
                                        int=network.network_address
                                        if network.network_address == IPv4Address(self.DEFAULT_NETWORK)
                                        else network.with_prefixlen)

            forwarders = []

            for forwarder in self._forwarders.value.split(u','):
                forwarder = forwarder.strip()

                if valid_ipv4(forwarder):
                    forwarders.append(forwarder)

            self.cfg[key] = forwarders

            self.parent.master.exit()

        except Exception as err:
            logging.error(u'Cannot save record')
            logging.exception(err)
            showerror(title=u'Save Failed',
                      message=u'Cannot Save forwarder: {err}'.format(err=err))

    def _cancel(self):
        self.parent.master.exit()

    @property
    def tooltip(self):
        tooltip_text = u"Example:\n"

        example = OrderedDict()
        example[u'Interface'] = u'192.168.1.0'
        example[u'Forwarders'] = u'208.67.222.222, 208.67.220.220'

        tooltip_text += Table.init_from_tree(example,
                                             title=make_multi_line_list(u'Requests arriving at 192.168.1.0 are '
                                                                        u'resolved using the opendns nameservers '
                                                                        u'208.67.222.222 and 208.67.220.220'),
                                             table_format=Table.LIGHT_TABLE_FORMAT).text()

        return tooltip_text
