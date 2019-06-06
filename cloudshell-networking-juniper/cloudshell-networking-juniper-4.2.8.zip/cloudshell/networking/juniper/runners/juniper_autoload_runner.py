#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.runners.autoload_runner import AutoloadRunner
from cloudshell.networking.juniper.flows.juniper_autoload_flow import JuniperSnmpAutoloadFlow


class JuniperAutoloadRunner(AutoloadRunner):
    def __init__(self, cli_handler, snmp_handler, logger, resource_config):
        super(JuniperAutoloadRunner, self).__init__(resource_config, logger)
        self._cli_handler = cli_handler
        self._snmp_handler = snmp_handler

    @property
    def autoload_flow(self):
        return JuniperSnmpAutoloadFlow(self._snmp_handler, self._logger)
