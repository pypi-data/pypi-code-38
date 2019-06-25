__copyright__ = "# Copyright (c) 2016 by cisco Systems, Inc. All rights reserved."
__author__ = "Myles Dear <mdear@cisco.com>"

from .statemachine import NxosvSingleRpStateMachine
from .connection_provider import NxosvSingleRpConnectionProvider
from unicon.plugins.nxos import NxosServiceList
from unicon.plugins.nxos import BaseNxosSingleRpConnection
from unicon.plugins.nxos.nxosv.setting import NxosvSettings

class NxosvSingleRpConnection(BaseNxosSingleRpConnection):
    os = 'nxos'
    series = 'nxosv'
    chassis_type = 'single_rp'
    state_machine_class = NxosvSingleRpStateMachine
    connection_provider_class = NxosvSingleRpConnectionProvider
    subcommand_list = NxosServiceList
    settings = NxosvSettings()

