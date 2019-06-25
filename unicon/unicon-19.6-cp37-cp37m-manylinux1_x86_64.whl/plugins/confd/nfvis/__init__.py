__copyright__ = "# Copyright (c) 2017 by cisco Systems, Inc. All rights reserved."
__author__ = "Dave Wapstra <dwapstra@cisco.com>"


from unicon.plugins.confd import ConfdServiceList, ConfdConnection, ConfdConnectionProvider
from .statemachine import NfvisStateMachine
from unicon.plugins.confd.settings import ConfdSettings


class NfvisServiceList(ConfdServiceList):
    def __init__(self):
        super().__init__()
        delattr(self, 'cli_style')


class NfvisSingleRPConnection(ConfdConnection):
    os = 'confd'
    series = 'nfvis'
    chassis_type = 'single_rp'
    state_machine_class = NfvisStateMachine
    connection_provider_class = ConfdConnectionProvider
    subcommand_list = NfvisServiceList
    settings = ConfdSettings()
