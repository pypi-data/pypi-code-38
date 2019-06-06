#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.runners.connectivity_runner import ConnectivityRunner
from cloudshell.networking.juniper.flows.juniper_add_vlan_flow import JuniperAddVlanFlow
from cloudshell.networking.juniper.flows.juniper_remove_vlan_flow import JuniperRemoveVlanFlow


class JuniperConnectivityRunner(ConnectivityRunner):
    def __init__(self, cli_handler, logger):
        """ Handle add/remove vlan flows
            :param cli_handler:
            :param logger:
            """

        super(JuniperConnectivityRunner, self).__init__(logger, cli_handler)

    @property
    def remove_vlan_flow(self):
        return JuniperRemoveVlanFlow(self.cli_handler, self._logger)

    @property
    def add_vlan_flow(self):
        return JuniperAddVlanFlow(self.cli_handler, self._logger)
