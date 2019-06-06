#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.runners.firmware_runner import FirmwareRunner
from cloudshell.networking.juniper.flows.juniper_firmware_flow import JuniperFirmwareFlow


class JuniperFirmwareRunner(FirmwareRunner):
    def __init__(self, cli_handler, logger):
        super(JuniperFirmwareRunner, self).__init__(logger, cli_handler)

    @property
    def load_firmware_flow(self):
        return JuniperFirmwareFlow(self.cli_handler, self._logger)
