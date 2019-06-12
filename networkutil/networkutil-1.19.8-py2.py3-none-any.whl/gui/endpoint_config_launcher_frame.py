# encoding: utf-8

import logging_helper
from uiutil.frame.dynamic import add_layout_config, LAYOUT_CFG, DynamicFrame
from ..resources import templates
from .environments_window import EnvironmentsChildWindow
from .api_window import APIChildWindow
from .endpoint_window import EndpointsChildWindow

logging = logging_helper.setup_logging()

ROOT_LAYOUT = u'{c}.root_layouts.endpoint_launcher_layout'.format(c=LAYOUT_CFG)


class EndpointsLauncherFrame(DynamicFrame):

    def __init__(self,
                 *args,
                 **kwargs):
        # Set the config initialisation parameters
        add_layout_config(templates.endpoint_launcher_layout)

        super(EndpointsLauncherFrame, self).__init__(*args, **kwargs)

    def launch_env(self):
        window = EnvironmentsChildWindow(fixed=True,
                                         parent_geometry=self.parent.winfo_toplevel().winfo_geometry())

        self.modal_window(window)

    def launch_api(self):
        window = APIChildWindow(fixed=True,
                                parent_geometry=self.parent.winfo_toplevel().winfo_geometry())

        self.modal_window(window)

    def launch_endpoint(self):
        window = EndpointsChildWindow(fixed=True,
                                      parent_geometry=self.parent.winfo_toplevel().winfo_geometry())

        self.modal_window(window)
