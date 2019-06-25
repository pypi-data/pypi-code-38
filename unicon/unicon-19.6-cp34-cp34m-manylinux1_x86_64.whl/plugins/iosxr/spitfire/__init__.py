
__copyright__ = "# Copyright (c) 2018 by cisco Systems, Inc. All rights reserved."
__author__ = "Sritej K V R <skanakad@cisco.com>"

from unicon.bases.routers.connection import BaseSingleRpConnection
from unicon.bases.routers.connection import BaseDualRpConnection

from unicon.plugins.iosxr import service_implementation as svc
from unicon.plugins.iosxe.service_implementation import Ping as IosXePing

from unicon.plugins.iosxr.spitfire.statemachine import SpitfireSingleRpStateMachine
from unicon.plugins.iosxr.spitfire.connection_provider import SpitfireSingleRpConnectionProvider
from unicon.plugins.iosxr.spitfire.settings import SpitfireSettings


from unicon.plugins.generic import ServiceList

class SpitfireServiceList(ServiceList):
    def __init__(self):
        super().__init__()
        self.configure = svc.Configure
        self.attach_console = svc.AttachModuleConsole
        self.bash_console = svc.BashService
        self.ping = IosXePing

class SpitfireSingleRpConnection(BaseSingleRpConnection):
    os = 'iosxr'
    series = 'spitfire'
    chassis_type = 'single_rp'
    state_machine_class = SpitfireSingleRpStateMachine
    connection_provider_class = SpitfireSingleRpConnectionProvider
    subcommand_list = SpitfireServiceList
    settings = SpitfireSettings()

