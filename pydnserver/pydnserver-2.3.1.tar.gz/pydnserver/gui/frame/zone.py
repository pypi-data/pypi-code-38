# encoding: utf-8

import logging_helper
from uiutil.tk_names import HORIZONTAL, W, NSEW, askquestion
from uiutil import BaseFrame, Position, Label, Separator, RadioButton, Switch, Button
from configurationutil import Configuration
from ...config import dns_lookup
from ..window.record import AddEditRecordWindow

logging = logging_helper.setup_logging()


class ZoneRecordsFrame(BaseFrame):

    def __init__(self,
                 cfg,
                 address_list,
                 *args,
                 **kwargs):
        """
        :param cfg: Configuration object
        :param address_list:
        :param args:
        :param kwargs:
        """

        BaseFrame.__init__(self,
                           layout=HORIZONTAL,
                           *args,
                           **kwargs)

        self.cfg = cfg
        self._address_list = address_list

        self.dns_active_list = {}

        self.columnconfigure(self.column.current, weight=1)

        Label(text=u'Host',
              sticky=W)

        Label(text=u'Redirect',
              sticky=W)

        Label(text=u'Active',
              sticky=W)

        Separator()

        value_set = False
        for host, host_config in iter(dns_lookup.get_redirection_config().items()):

            dns_host_display_name = self._lookup_display_name(host)
            text = (dns_host_display_name
                    if dns_host_display_name
                    else host)

            self.selected_record = RadioButton(text=text,
                                               value=host,
                                               row=Position.NEXT,
                                               sticky=W,
                                               tooltip=(host
                                                        if dns_host_display_name
                                                        else u''))
            if not value_set:
                self.selected_record.value = host
                value_set = True

            # Get the configured record
            dns_redirect_host = host_config[u'redirect_host']
            dns_redirect_display_name = self._lookup_display_name(dns_redirect_host)

            Label(text=(dns_redirect_display_name
                        if dns_redirect_display_name
                        else dns_redirect_host),
                  sticky=W,
                  tooltip=dns_redirect_host if dns_redirect_display_name else u'')

            self.dns_active_list[host] = Switch(switch_state=host_config[u'active'],
                                                command=(lambda hst=host:
                                                         self._update_active(host=hst)),
                                                sticky=W)

        Separator()

        self.nice_grid()

    def _lookup_display_name(self,
                             address):

        display_name = u''

        # Check for a display name for host, accepting first match!
        for addr in self._address_list:
            if isinstance(addr, tuple):
                if address == addr[0] and addr[1]:
                    display_name = addr[1]
                    break  # We found our name so move on!

        return display_name

    def _update_active(self,
                       host):
        key = u'{c}.{h}.{active}'.format(c=dns_lookup.DNS_LOOKUP_CFG,
                                         h=host,
                                         active=dns_lookup.ACTIVE)

        self.cfg[key] = self.dns_active_list[host].switched_on


class ZoneConfigFrame(BaseFrame):

    AUTO_POSITION = HORIZONTAL
    BUTTON_WIDTH = 15

    def __init__(self,
                 address_list=None,
                 *args,
                 **kwargs):

        """

        :param address_list: (list)  List of domains to provide the user in the combobox.
                                     Each entry in the list can be either:
                                         --> (string) containing the domain name
                                         --> (tuple)  containing the domain name and a display name
                                                      e.g. ('google.co.uk', 'Google')
        :param args:
        :param kwargs:
        """

        BaseFrame.__init__(self,
                           *args,
                           **kwargs)

        self.cfg = Configuration()

        self._address_list = [] if address_list is None else address_list

        self.zone_records_frame_position = dict(row=self.row.current,
                                                column=self.row.current,
                                                sticky=NSEW)
        self._add_buttons()
        self.zone_records_frame_position['columnspan'] = self.column.max
        self._build_zone_records_frame()
        self.nice_grid()

    def _build_zone_records_frame(self):
        try:
            self.zone_records.destroy()
        except AttributeError:
            pass
        self.zone_records = ZoneRecordsFrame(cfg=self.cfg,
                                             address_list=self._address_list,
                                             **self.zone_records_frame_position)

    def _add_buttons(self):

        Button(row=Position.NEXT,
               text=u'Delete Record',
               width=self.BUTTON_WIDTH,
               command=self._delete_zone_record,
               tooltip=u'Delete\nselected\nrecord')

        Button(text=u'Add Record',
               width=self.BUTTON_WIDTH,
               command=self._add_zone_record,
               tooltip=u'Add record\nto dns list')

        Button(text=u'Edit Record',
               width=self.BUTTON_WIDTH,
               command=self._edit_zone_record,
               tooltip=u'Edit\nselected\nrecord')

    @property
    def selected_record(self):
        return self.zone_records.selected_record.value

    def _add_zone_record(self):
        window = AddEditRecordWindow(fixed=True,
                                     parent_geometry=(self.parent.winfo_toplevel().winfo_geometry()),
                                     address_list=self._address_list)

        window.transient()
        window.grab_set()
        self.parent.wait_window(window)

        self._build_zone_records_frame()

        self.parent.master.update_geometry()

    def _edit_zone_record(self):
        window = AddEditRecordWindow(selected_record=self.selected_record,
                                     edit=True,
                                     fixed=True,
                                     parent_geometry=(self.parent.winfo_toplevel().winfo_geometry()),
                                     address_list=self._address_list)

        window.transient()
        window.grab_set()
        self.parent.wait_window(window)

        self._build_zone_records_frame()

        self.parent.master.update_geometry()

    def _delete_zone_record(self):
        result = askquestion(title=u"Delete Record",
                             message=u"Are you sure you "
                                     u"want to delete {r}?".format(r=self.selected_record),
                             icon=u'warning',
                             parent=self)

        if result == u'yes':
            key = u'{c}.{h}'.format(c=dns_lookup.DNS_LOOKUP_CFG,
                                    h=self.selected_record)

            del self.cfg[key]

            self._build_zone_records_frame()

            self.parent.master.update_geometry()
