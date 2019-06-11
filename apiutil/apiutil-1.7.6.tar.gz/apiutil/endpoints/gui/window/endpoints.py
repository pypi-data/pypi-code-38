# encoding: utf-8

import logging_helper
from uiutil import ChildWindow
from uiutil.tk_names import NSEW
from ..frame.endpoints import EndpointConfigFrame

logging = logging_helper.setup_logging()


class EndpointConfigWindow(ChildWindow):

    def _draw_widgets(self):
        self.title(u"Endpoint Configuration")

        self.config = EndpointConfigFrame(parent=self._main_frame,
                                          sticky=NSEW)
