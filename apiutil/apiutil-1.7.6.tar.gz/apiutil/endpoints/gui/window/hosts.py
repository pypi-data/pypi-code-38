# encoding: utf-8

import logging_helper
from uiutil import ChildWindow
from uiutil.tk_names import NSEW
from ..frame.hosts import HostConfigFrame

logging = logging_helper.setup_logging()


class HostConfigWindow(ChildWindow):

    def _draw_widgets(self):
        self.title(u"Host Configuration")

        self.config = HostConfigFrame(parent=self._main_frame,
                                      sticky=NSEW)
