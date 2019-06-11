# encoding: utf-8

import logging_helper
from uiutil import ChildWindow
from uiutil.tk_names import NSEW
from ..frame.endpoint import AddEditEndpointFrame

logging = logging_helper.setup_logging()


class AddEditEndpointWindow(ChildWindow):

    def __init__(self,
                 selected_record=None,
                 edit=False,
                 *args,
                 **kwargs):

        self.selected_record = selected_record
        self.edit = edit

        super(AddEditEndpointWindow, self).__init__(*args,
                                                    **kwargs)

    def _draw_widgets(self):
        self.title(u"Add/Edit Endpoint")

        self.config = AddEditEndpointFrame(parent=self._main_frame,
                                           selected_record=self.selected_record,
                                           edit=self.edit,
                                           sticky=NSEW)
