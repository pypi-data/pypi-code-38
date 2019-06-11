# encoding: utf-8

import logging_helper
from uiutil import ChildWindow
from uiutil.tk_names import NSEW
from ..frame.apis import APIConfigFrame

logging = logging_helper.setup_logging()


class APIConfigWindow(ChildWindow):

    def _draw_widgets(self):
        self.title(u"API Configuration")

        self.config = APIConfigFrame(parent=self._main_frame,
                                     sticky=NSEW)
