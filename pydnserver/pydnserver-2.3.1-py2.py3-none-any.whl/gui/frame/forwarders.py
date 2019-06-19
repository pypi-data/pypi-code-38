# encoding: utf-8

import logging_helper
from uiutil.tk_names import HORIZONTAL, W, NSEW, askquestion, showerror
from uiutil import BaseFrame, Button, Separator, Label, Position, RadioButton
from configurationutil import Configuration
from ...config import dns_forwarders
from ..window.forwarder import AddEditForwarderWindow, AddEditForwarderFrame

logging = logging_helper.setup_logging()


class RecordFrame(BaseFrame):

    def __init__(self,
                 selected=None,
                 *args,
                 **kwargs):

        BaseFrame.__init__(self,
                           layout=HORIZONTAL,
                           *args,
                           **kwargs)

        Label(text=u'Network',
              sticky=W)

        Label(text=u'Forwarders',
              sticky=W)

        Separator()

        for interface, forwarders in iter(dns_forwarders.get_all_forwarders().items()):
            self.radio_button = RadioButton(text=interface,
                                            value=interface,
                                            row=Position.NEXT,
                                            sticky=W)
            if selected == interface or selected is None:
                selected = interface

            Label(text=u', '.join(forwarders),
                  sticky=W)

        self.radio_button.value = selected

        Separator()

        self.nice_grid()

    @property
    def selected_record(self):
       return self.radio_button.value


class ForwarderConfigFrame(BaseFrame):

    BUTTON_WIDTH = 15

    def __init__(self,
                 *args,
                 **kwargs):

        BaseFrame.__init__(self,
                           layout=HORIZONTAL,
                           *args,
                           **kwargs)

        self.cfg = Configuration()

        self.nameserver_radio_list = {}

        self.record_frame_kwargs = dict(row=self.row.current,
                                        column=self.column.current,
                                        sticky=NSEW)
        self._add_buttons()

        self.record_frame_kwargs['columnspan'] = self.column.max

        self._build_record_frame()

        self.nice_grid()

    def _build_record_frame(self,
                            selected=None):
        self.record_frame = RecordFrame(selected=selected,
                                        **self.record_frame_kwargs)

    @property
    def selected_record(self):
       return self.record_frame.selected_record

    def _add_buttons(self):

        Button(text=u'Delete',
               width=self.BUTTON_WIDTH,
               command=self._delete_forwarder,
               row=Position.NEXT)

        Button(text=u'Add',
               width=self.BUTTON_WIDTH,
               command=self._add_forwarder)

        Button(text=u'Edit',
               width=self.BUTTON_WIDTH,
               command=self._edit_forwarder)

    def _refresh(self):
        selected = self.selected_record
        self.record_frame.destroy()
        self._build_record_frame(selected=selected)
        self.nice_grid()
        self.parent.master.update_geometry()

    def _add_forwarder(self):
        window = AddEditForwarderWindow(fixed=True,
                                        parent_geometry=self.parent.winfo_toplevel().winfo_geometry())

        window.transient()
        window.grab_set()
        self.parent.wait_window(window)
        self._refresh()

    def _edit_forwarder(self):
        window = AddEditForwarderWindow(selected_record=self.selected_record,
                                        edit=True,
                                        fixed=True,
                                        parent_geometry=self.parent.winfo_toplevel().winfo_geometry())
        window.transient()
        window.grab_set()
        self.parent.wait_window(window)
        self._refresh()

    def _delete_forwarder(self):
        selected = self.selected_record

        if selected == AddEditForwarderFrame.DEFAULT_NETWORK:
            showerror(title=u'Default Forwarder',
                      message=u'You cannot delete the default forwarder!')

        else:
            result = askquestion(u"Delete Record",
                                 u"Are you sure you want to delete {r}?".format(r=selected),
                                 icon=u'warning',
                                 parent=self)

            if result == u'yes':
                key = u'{cfg}.{int}'.format(cfg=dns_forwarders.DNS_SERVERS_CFG,
                                            int=selected)
                del self.cfg[key]

                self._refresh()
