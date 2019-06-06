from cloudshell.cli.session.session_exceptions import CommandExecutionException
from cloudshell.devices.flows.cli_action_flows import EnableSnmpFlow
from cloudshell.networking.juniper.cli.juniper_cli_handler import JuniperCliHandler
from cloudshell.networking.juniper.command_actions.commit_rollback_actions import CommitRollbackActions
from cloudshell.networking.juniper.command_actions.enable_disable_snmp_actions import EnableDisableSnmpActions
from cloudshell.networking.juniper.command_actions.enable_disable_snmp_v3_actions import EnableDisableSnmpV3Actions
from cloudshell.snmp.snmp_parameters import SNMPV2WriteParameters, SNMPV3Parameters


class JuniperEnableSnmpFlow(EnableSnmpFlow):
    def __init__(self, cli_handler, logger):
        """
        Enable snmp flow
        :param cli_handler:
        :type cli_handler: JuniperCliHandler
        :param logger:
        :return:
        """
        super(JuniperEnableSnmpFlow, self).__init__(cli_handler, logger)
        self._cli_handler = cli_handler

    def execute_flow(self, snmp_parameters):
        with self._cli_handler.config_mode_service() as cli_service:
            if isinstance(snmp_parameters, SNMPV3Parameters):
                self._enable_snmp_v3(cli_service, snmp_parameters)
            else:
                self._enable_snmp(cli_service, snmp_parameters)

    def _enable_snmp(self, cli_service, snmp_parameters):
        """
        :type cli_service: cloudshell.cli.cli_service_impl.CliServiceImpl
        :type snmp_parameters: cloudshell.snmp.snmp_parameters.SNMPParameters
        """
        snmp_community = snmp_parameters.snmp_community
        if not snmp_community:
            raise Exception("SNMP Community has to be defined")
        snmp_actions = EnableDisableSnmpActions(cli_service, self._logger)
        commit_rollback = CommitRollbackActions(cli_service, self._logger)
        if not snmp_actions.configured(snmp_community):
            self._logger.debug('Configuring SNMP with community {}'.format(snmp_community))
            try:
                output = snmp_actions.enable_snmp(snmp_community,
                                                  write=isinstance(snmp_parameters, SNMPV2WriteParameters))
                output += commit_rollback.commit()
                return output
            except CommandExecutionException:
                commit_rollback.rollback()
                self._logger.exception('Failed to enable SNMP')
                raise

    def _enable_snmp_v3(self, cli_service, snmp_parameters):
        """
        :type cli_service: cloudshell.cli.cli_service_impl.CliServiceImpl
        :type snmp_parameters: cloudshell.snmp.snmp_parameters.SNMPV3Parameters
        """
        snmp_v3_actions = EnableDisableSnmpV3Actions(cli_service, self._logger)
        commit_rollback = CommitRollbackActions(cli_service, self._logger)
        snmp_user = snmp_parameters.snmp_user
        snmp_password = snmp_parameters.snmp_password
        snmp_priv_key = snmp_parameters.snmp_private_key
        snmp_auth_proto = snmp_parameters.auth_protocol
        snmp_priv_proto = snmp_parameters.private_key_protocol
        self._logger.debug('Enable SNMPv3')
        try:
            output = snmp_v3_actions.enable_snmp_v3(snmp_user, snmp_password, snmp_priv_key, snmp_auth_proto,
                                                    snmp_priv_proto)
            commit_rollback.commit()
            return output
        except CommandExecutionException:
            commit_rollback.rollback()
            self._logger.exception('Failed to enable SNMPv3')
            raise
