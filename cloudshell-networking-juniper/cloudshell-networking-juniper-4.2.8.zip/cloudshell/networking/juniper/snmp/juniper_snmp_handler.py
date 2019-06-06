from cloudshell.devices.snmp_handler import SnmpHandler
from cloudshell.networking.juniper.flows.juniper_disable_snmp_flow import JuniperDisableSnmpFlow
from cloudshell.networking.juniper.flows.juniper_enable_snmp_flow import JuniperEnableSnmpFlow


class JuniperSnmpHandler(SnmpHandler):
    def __init__(self, cli_handler, resource_config, logger, api):
        super(JuniperSnmpHandler, self).__init__(resource_config, logger, api)
        self._cli_handler = cli_handler

    def _create_enable_flow(self):
        return JuniperEnableSnmpFlow(self._cli_handler, self._logger)

    def _create_disable_flow(self):
        return JuniperDisableSnmpFlow(self._cli_handler, self._logger)
