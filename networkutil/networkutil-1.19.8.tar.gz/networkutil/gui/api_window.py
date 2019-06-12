# encoding: utf-8

from uiutil.window.dynamic import DynamicRootWindow, DynamicChildWindow
from .api_frame import APIFrame, ROOT_LAYOUT


class _APIWindow(object):

    def __init__(self,
                 layout_key=ROOT_LAYOUT,
                 window_title=u'API Config',
                 *args,
                 **kwargs):
        super(_APIWindow, self).__init__(layout_key=layout_key,
                                         window_title=window_title,
                                         *args,
                                         **kwargs)

    def _draw_widgets(self):
        self.title(self.window_title)
        self.dynamic_frame = APIFrame(parent=self._main_frame,
                                      layout_key=self.key,
                                      item_dict=self.item_dict)


class APIRootWindow(_APIWindow, DynamicRootWindow):

    def __init__(self, *args, **kwargs):
        super(APIRootWindow, self).__init__(*args, **kwargs)


class APIChildWindow(_APIWindow, DynamicChildWindow):

    def __init__(self, *args, **kwargs):
        super(APIChildWindow, self).__init__(*args, **kwargs)
