__copyright__ = "# Copyright (c) 2016 by cisco Systems, Inc. All rights reserved."
__author__ = "Myles Dear <mdear@cisco.com>"


from unicon.plugins.iosxe import IosXEServiceList, IosXESingleRpConnection
from unicon.plugins.iosxe.csr1000v import service_implementation as svc
from .statemachine import Csr1000vSingleRpStateMachine
from .settings import Csr1000vSettings


class Csr1000vServiceList(IosXEServiceList):
    def __init__(self):
        super().__init__()
        self.reload = svc.Reload
        self.shellexec = svc.Shell
        self.config = svc.Config
        self.configure = svc.Configure
        self.execute = svc.Execute
        self.rommon = svc.Rommon


class Csr1000vSingleRpConnection(IosXESingleRpConnection):
    os = 'iosxe'
    series = 'csr1000v'
    chassis_type = 'single_rp'
    state_machine_class = Csr1000vSingleRpStateMachine
    subcommand_list = Csr1000vServiceList
    settings = Csr1000vSettings()
