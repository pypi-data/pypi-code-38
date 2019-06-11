# encoding: utf-8

from uiutil import RootWindow, ChildWindow
from ..frame.config import APIEndpointsConfigFrame


class _APIEndpointsConfigWindow(object):

    def _draw_widgets(self):
        self.title(u'Endpoints Config')
        self.dynamic_frame = APIEndpointsConfigFrame()


class APIEndpointsConfigRootWindow(_APIEndpointsConfigWindow, RootWindow):
    pass


class APIEndpointsConfigChildWindow(_APIEndpointsConfigWindow, ChildWindow):
    pass
