from cloudshell.cli.command_template.command_template import CommandTemplate
from cloudshell.networking.juniper.command_templates.generic_action_error_map import ACTION_MAP, ERROR_MAP

CREATE_VIEW = CommandTemplate('set snmp view SNMPSHELLVIEW oid .1 include', action_map=ACTION_MAP, error_map=ERROR_MAP)

ENABLE_SNMP_READ = CommandTemplate('set snmp community {snmp_community} authorization read-only view SNMPSHELLVIEW',
                                   action_map=ACTION_MAP,
                                   error_map=ERROR_MAP)
ENABLE_SNMP_WRITE = CommandTemplate('set snmp community {snmp_community} authorization read-write view SNMPSHELLVIEW',
                                    action_map=ACTION_MAP,
                                    error_map=ERROR_MAP)
DELETE_VIEW = CommandTemplate('delete snmp view SNMPSHELLVIEW', action_map=ACTION_MAP, error_map=ERROR_MAP)
DISABLE_SNMP = CommandTemplate('delete snmp community {snmp_community}', action_map=ACTION_MAP, error_map=ERROR_MAP)

SHOW_SNMP_COMMUNITY = CommandTemplate('show snmp community {snmp_community}', action_map=ACTION_MAP,
                                      error_map=ERROR_MAP)
