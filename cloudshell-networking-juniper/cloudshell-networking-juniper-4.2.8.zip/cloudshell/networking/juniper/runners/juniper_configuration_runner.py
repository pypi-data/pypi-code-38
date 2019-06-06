#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.runners.configuration_runner import ConfigurationRunner
from cloudshell.networking.juniper.flows.juniper_restore_flow import JuniperRestoreFlow
from cloudshell.networking.juniper.flows.juniper_save_flow import JuniperSaveFlow


class JuniperConfigurationRunner(ConfigurationRunner):
    def __init__(self, cli_handler, logger, resource_config, api):
        super(JuniperConfigurationRunner, self).__init__(logger, resource_config, api, cli_handler)

    @property
    def restore_flow(self):
        return JuniperRestoreFlow(self.cli_handler, self._logger)

    @property
    def save_flow(self):
        return JuniperSaveFlow(self.cli_handler, self._logger)

    @property
    def file_system(self):
        return "local:"
