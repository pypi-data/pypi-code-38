# encoding: utf-8

import logging_helper
from uiutil import ChildWindow
from uiutil.tk_names import NSEW
from ..frame.environments import EnvironmentConfigFrame

logging = logging_helper.setup_logging()


class EnvironmentConfigWindow(ChildWindow):

    def _draw_widgets(self):
        self.title(u"Environment Configuration")

        self.config = EnvironmentConfigFrame(parent=self._main_frame,
                                             sticky=NSEW)
