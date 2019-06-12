# encoding: utf-8

from uiutil.window.dynamic import DynamicRootWindow, DynamicChildWindow
from .endpoint_config_launcher_frame import EndpointsLauncherFrame, ROOT_LAYOUT


class _EndpointsLauncherWindow(object):

    def __init__(self,
                 layout_key=ROOT_LAYOUT,
                 window_title=u'Endpoint Launcher Config',
                 *args,
                 **kwargs):
        super(_EndpointsLauncherWindow, self).__init__(layout_key=layout_key,
                                                       window_title=window_title,
                                                       *args,
                                                       **kwargs)

    def _draw_widgets(self):
        self.title(self.window_title)
        self.dynamic_frame = EndpointsLauncherFrame(parent=self._main_frame,
                                                    layout_key=self.key,
                                                    item_dict=self.item_dict)


class EndpointsLauncherRootWindow(_EndpointsLauncherWindow, DynamicRootWindow):

    def __init__(self, *args, **kwargs):
        super(EndpointsLauncherRootWindow, self).__init__(*args, **kwargs)


class EndpointsLauncherChildWindow(_EndpointsLauncherWindow, DynamicChildWindow):

    def __init__(self, *args, **kwargs):
        super(EndpointsLauncherChildWindow, self).__init__(*args, **kwargs)
