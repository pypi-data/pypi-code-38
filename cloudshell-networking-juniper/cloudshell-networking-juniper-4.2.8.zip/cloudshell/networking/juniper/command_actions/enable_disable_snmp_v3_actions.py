from cloudshell.cli.cli_service_impl import CliServiceImpl as CliService
from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor
from cloudshell.networking.juniper.command_templates import enable_disable_snmp_v3 as command_template
from cloudshell.snmp.snmp_parameters import SNMPV3Parameters


class EnableDisableSnmpV3Actions(object):
    # AUTH_NO_AUTH = "No Authentication Protocol"
    # AUTH_MD5 = "MD5"
    # AUTH_SHA = "SHA"
    #
    # PRIV_NO_PRIV = "No Privacy Protocol"
    # PRIV_DES = "DES"
    # PRIV_3DES = "3DES-EDE"
    # PRIV_AES128 = "AES-128"
    # PRIV_AES192 = "AES-192"
    # PRIV_AES256 = "AES-256"

    AUTH_COMMAND_TABLE = {
        SNMPV3Parameters.AUTH_NO_AUTH: command_template.SET_AUTH_NONE,
        SNMPV3Parameters.AUTH_MD5: command_template.SET_AUTH_MD5,
        SNMPV3Parameters.AUTH_SHA: command_template.SET_AUTH_SHA
    }
    PRIV_COMMAND_TABLE = {
        SNMPV3Parameters.PRIV_NO_PRIV: command_template.SET_PRIV_NONE,
        SNMPV3Parameters.PRIV_DES: command_template.SET_PRIV_DES,
        SNMPV3Parameters.PRIV_3DES: command_template.SET_PRIV_3DES,
        SNMPV3Parameters.PRIV_AES128: command_template.SET_PRIV_AES128,
        SNMPV3Parameters.PRIV_AES192: command_template.SET_PRIV_AES192,
        SNMPV3Parameters.PRIV_AES256: command_template.SET_PRIV_AES256
    }

    ACCESS_VIEW_COMMAND_LIST = [command_template.SET_ACCESS_NONE_READ, command_template.SET_ACCESS_NONE_WRITE,
                                command_template.SET_ACCESS_AUTH_READ, command_template.SET_ACCESS_AUTH_WRITE,
                                command_template.SET_ACCESS_PRIV_READ, command_template.SET_ACCESS_PRIV_WRITE]

    SNMPV3_GROUP = 'SHELLSSNMPV3GROUP'
    SNMPV3_VIEW = 'SHELLSSNMPV3VIEW'

    def __init__(self, cli_service, logger):
        """
        Reboot actions
        :param cli_service: config mode cli service
        :type cli_service: CliService
        :param logger:
        :type logger: Logger
        :return:
        """
        self._cli_service = cli_service
        self._logger = logger

    def enable_snmp_v3(self, snmp_user, snmp_password, snmp_priv_key, auth_proto, priv_proto):
        """
        Enable snmp v3 on the device
        :return:
        """
        auth_command_template = self.AUTH_COMMAND_TABLE.get(auth_proto)
        if not auth_command_template:
            raise Exception(self.__class__.__name__, 'Authentication protocol {} is not supported'.format(auth_proto))
        priv_command_template = self.PRIV_COMMAND_TABLE.get(priv_proto)
        if not priv_command_template:
            raise Exception(self.__class__.__name__, 'Privacy Protocol {} is not supported'.format(priv_proto))

        out = CommandTemplateExecutor(self._cli_service, auth_command_template).execute_command(user=snmp_user,
                                                                                                password=snmp_password)
        out += CommandTemplateExecutor(self._cli_service, priv_command_template).execute_command(user=snmp_user,
                                                                                                 password=snmp_priv_key)
        out += CommandTemplateExecutor(self._cli_service,
                                       command_template.SET_GROUP).execute_command(user=snmp_user,
                                                                                   group=self.SNMPV3_GROUP)
        out += CommandTemplateExecutor(self._cli_service, command_template.CREATE_VIEW).execute_command(
            view=self.SNMPV3_VIEW)
        for template in self.ACCESS_VIEW_COMMAND_LIST:
            out += CommandTemplateExecutor(self._cli_service, template).execute_command(group=self.SNMPV3_GROUP,
                                                                                        view=self.SNMPV3_VIEW)
        return out

    def disable_snmp_v3(self, snmp_user):
        """
        Disable snmp v3
        """
        out = CommandTemplateExecutor(self._cli_service, command_template.DELETE_GROUP_SECURITY).execute_command(
            user=snmp_user, group=self.SNMPV3_GROUP)
        out += CommandTemplateExecutor(self._cli_service, command_template.DELETE_GROUP_ACCESS).execute_command(
            group=self.SNMPV3_GROUP)
        out += CommandTemplateExecutor(self._cli_service, command_template.DELETE_VIEW).execute_command(
            view=self.SNMPV3_VIEW)
        out += CommandTemplateExecutor(self._cli_service, command_template.DELETE_USER).execute_command(user=snmp_user)
        return out
