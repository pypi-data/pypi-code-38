# encoding: utf-8

import logging_helper
from tkinter.constants import NSEW
from uiutil.window.child import ChildWindow
from ..frame.record import AddEditRecordFrame

logging = logging_helper.setup_logging()


class AddEditRecordWindow(ChildWindow):

    def __init__(self,
                 selected_record=None,
                 edit=False,
                 address_list=None,
                 *args,
                 **kwargs):

        self.selected_record = selected_record
        self.edit = edit
        self.address_list = address_list

        super(AddEditRecordWindow, self).__init__(*args,
                                                  **kwargs)

    def _draw_widgets(self):
        self.title(u"Add/Edit DNS Record")

        self.config = AddEditRecordFrame(parent=self._main_frame,
                                         selected_record=self.selected_record,
                                         edit=self.edit,
                                         address_list=self.address_list)
        self.config.grid(sticky=NSEW)
