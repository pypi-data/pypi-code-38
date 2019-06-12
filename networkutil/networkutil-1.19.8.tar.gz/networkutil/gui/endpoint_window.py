# encoding: utf-8

from uiutil.window.dynamic import DynamicRootWindow, DynamicChildWindow
from .endpoint_frame import EndpointsFrame, ROOT_LAYOUT


class _EndpointsWindow(object):

    def __init__(self,
                 layout_key=ROOT_LAYOUT,
                 window_title=u'Endpoint Config',
                 *args,
                 **kwargs):
        super(_EndpointsWindow, self).__init__(layout_key=layout_key,
                                               window_title=window_title,
                                               *args,
                                               **kwargs)

    def _draw_widgets(self):
        self.title(self.window_title)
        self.dynamic_frame = EndpointsFrame(parent=self._main_frame,
                                            layout_key=self.key,
                                            item_dict=self.item_dict)


class EndpointsRootWindow(_EndpointsWindow, DynamicRootWindow):

    def __init__(self, *args, **kwargs):
        super(EndpointsRootWindow, self).__init__(*args, **kwargs)


class EndpointsChildWindow(_EndpointsWindow, DynamicChildWindow):

    def __init__(self, *args, **kwargs):
        super(EndpointsChildWindow, self).__init__(*args, **kwargs)
