# encoding: utf-8

import logging_helper
from uiutil import ChildWindow
from uiutil.tk_names import NSEW
from ..frame.environment import AddEditEnvironmentFrame

logging = logging_helper.setup_logging()


class AddEditEnvironmentWindow(ChildWindow):

    def __init__(self,
                 selected_record=None,
                 edit=False,
                 *args,
                 **kwargs):

        self.selected_record = selected_record
        self.edit = edit

        super(AddEditEnvironmentWindow, self).__init__(*args,
                                                       **kwargs)

    def _draw_widgets(self):
        self.title(u"Add/Edit Environment")

        self.config = AddEditEnvironmentFrame(parent=self._main_frame,
                                              selected_record=self.selected_record,
                                              edit=self.edit,
                                              sticky=NSEW)
