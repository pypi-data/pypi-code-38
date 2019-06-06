from cloudshell.cli.session.session_exceptions import CommandExecutionException
from cloudshell.devices.flows.cli_action_flows import DisableSnmpFlow
from cloudshell.networking.juniper.cli.juniper_cli_handler import JuniperCliHandler
from cloudshell.networking.juniper.command_actions.commit_rollback_actions import CommitRollbackActions
from cloudshell.networking.juniper.command_actions.enable_disable_snmp_actions import EnableDisableSnmpActions
from cloudshell.networking.juniper.command_actions.enable_disable_snmp_v3_actions import EnableDisableSnmpV3Actions
from cloudshell.snmp.snmp_parameters import SNMPV3Parameters


class JuniperDisableSnmpFlow(DisableSnmpFlow):
    def __init__(self, cli_handler, logger):
        """
          Enable snmp flow
          :param cli_handler:
          :type cli_handler: JuniperCliHandler
          :param logger:
          :return:
          """
        super(JuniperDisableSnmpFlow, self).__init__(cli_handler, logger)
        self._cli_handler = cli_handler

    def execute_flow(self, snmp_parameters=None):
        with self._cli_handler.config_mode_service() as cli_service:
            if isinstance(snmp_parameters, SNMPV3Parameters):
                self._disable_snmp_v3(cli_service, snmp_parameters)
            else:
                self._disable_snmp(cli_service, snmp_parameters)

    def _disable_snmp(self, cli_service, snmp_parameters):
        snmp_community = snmp_parameters.snmp_community
        if not snmp_community:
            raise Exception("SNMP Community has to be defined")
        snmp_actions = EnableDisableSnmpActions(cli_service, self._logger)
        commit_rollback = CommitRollbackActions(cli_service, self._logger)
        try:
            self._logger.debug('Disable SNMP')
            snmp_actions.disable_snmp(snmp_community)
            commit_rollback.commit()
        except CommandExecutionException:
            commit_rollback.rollback()
            self._logger.exception('Failed to disable SNMP')
            raise

    def _disable_snmp_v3(self, cli_service, snmp_parameters):
        snmp_v3_actions = EnableDisableSnmpV3Actions(cli_service, self._logger)
        commit_rollback = CommitRollbackActions(cli_service, self._logger)
        snmp_user = snmp_parameters.snmp_user
        try:
            self._logger.debug('Disable SNMPv3')
            snmp_v3_actions.disable_snmp_v3(snmp_user)
            commit_rollback.commit()
        except CommandExecutionException:
            commit_rollback.rollback()
            self._logger.exception('Failed to enable SNMPv3')
            raise
