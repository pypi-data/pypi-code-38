# encoding: utf-8

from uiutil.window.dynamic import DynamicRootWindow, DynamicChildWindow
from .environments_frame import EnvironmentsFrame, ROOT_LAYOUT


class _EnvironmentsWindow(object):

    def __init__(self,
                 layout_key=ROOT_LAYOUT,
                 window_title=u'Env Config',
                 *args,
                 **kwargs):
        super(_EnvironmentsWindow, self).__init__(layout_key=layout_key,
                                                  window_title=window_title,
                                                  *args,
                                                  **kwargs)

    def _draw_widgets(self):
        self.title(self.window_title)
        self.dynamic_frame = EnvironmentsFrame(parent=self._main_frame,
                                               layout_key=self.key,
                                               item_dict=self.item_dict)


class EnvironmentsRootWindow(_EnvironmentsWindow, DynamicRootWindow):

    def __init__(self, *args, **kwargs):
        super(EnvironmentsRootWindow, self).__init__(*args, **kwargs)


class EnvironmentsChildWindow(_EnvironmentsWindow, DynamicChildWindow):

    def __init__(self, *args, **kwargs):
        super(EnvironmentsChildWindow, self).__init__(*args, **kwargs)
