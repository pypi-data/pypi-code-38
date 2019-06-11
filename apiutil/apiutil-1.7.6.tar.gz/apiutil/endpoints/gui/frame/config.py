# encoding: utf-8

import logging_helper
from configurationutil.gui import ConfigLauncherFrame
from ..window import HostConfigWindow, EndpointConfigWindow, APIConfigWindow, EnvironmentConfigWindow


logging = logging_helper.setup_logging()


class APIEndpointsConfigFrame(ConfigLauncherFrame):

    def __init__(self,
                 title=u'API Endpoints Config:',
                 *args,
                 **kwargs):

        config_windows = [
            {
                u'name': u'Hosts',
                u'class': HostConfigWindow
            },
            {
                u'name': u'Endpoints',
                u'class': EndpointConfigWindow
            },
            {
                u'name': u'APIs',
                u'class': APIConfigWindow
            },
            {
                u'name': u'Environments',
                u'class': EnvironmentConfigWindow
            }
        ]

        super(APIEndpointsConfigFrame, self).__init__(title=title,
                                                      config_windows=config_windows,
                                                      *args,
                                                      **kwargs)
