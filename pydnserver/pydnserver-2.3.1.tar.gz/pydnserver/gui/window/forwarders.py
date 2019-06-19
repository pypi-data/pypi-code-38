# encoding: utf-8

import logging_helper
from tkinter.constants import NSEW
from uiutil.window.child import ChildWindow
from ..frame.forwarders import ForwarderConfigFrame

logging = logging_helper.setup_logging()


class ForwarderConfigWindow(ChildWindow):

    def __init__(self,
                 *args,
                 **kwargs):
        super(ForwarderConfigWindow, self).__init__(*args,
                                                    **kwargs)

    def _draw_widgets(self):
        self.title(u"Forwarder Configuration")

        self.config = ForwarderConfigFrame(parent=self._main_frame)
        self.config.grid(sticky=NSEW)
