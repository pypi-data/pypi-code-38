from collections import OrderedDict

from cloudshell.cli.command_template.command_template import CommandTemplate
from cloudshell.networking.juniper.command_templates.generic_action_error_map import ACTION_MAP, ERROR_MAP

SET_AUTH_NONE = CommandTemplate('set snmp v3 usm local-engine user {user} authentication-none', action_map=ACTION_MAP,
                                error_map=ERROR_MAP)
SET_AUTH_SHA = CommandTemplate(
    'set snmp v3 usm local-engine user {user} authentication-sha authentication-password {password}',
    action_map=ACTION_MAP, error_map=ERROR_MAP)
SET_AUTH_MD5 = CommandTemplate(
    'set snmp v3 usm local-engine user {user} authentication-md5 authentication-password {password}',
    action_map=ACTION_MAP, error_map=ERROR_MAP)

_PRIV_ERROR_MAP = OrderedDict([(r'[Ll]ength\s\d+\sis\snot\swithin\srange', 'Private key is too short')])
_PRIV_ERROR_MAP.update(ERROR_MAP)

SET_PRIV_NONE = CommandTemplate('set snmp v3 usm local-engine user {user} privacy-none',
                                action_map=ACTION_MAP, error_map=ERROR_MAP)

SET_PRIV_DES = CommandTemplate('set snmp v3 usm local-engine user {user} privacy-des privacy-password {password}',
                               action_map=ACTION_MAP, error_map=_PRIV_ERROR_MAP)

SET_PRIV_3DES = CommandTemplate('set snmp v3 usm local-engine user {user} privacy-3des privacy-password {password}',
                                action_map=ACTION_MAP, error_map=_PRIV_ERROR_MAP)

SET_PRIV_AES128 = CommandTemplate('set snmp v3 usm local-engine user {user} privacy-aes128 privacy-password {password}',
                                  action_map=ACTION_MAP, error_map=_PRIV_ERROR_MAP)
SET_PRIV_AES192 = CommandTemplate('set snmp v3 usm local-engine user {user} privacy-aes192 privacy-password {password}',
                                  action_map=ACTION_MAP, error_map=_PRIV_ERROR_MAP)
SET_PRIV_AES256 = CommandTemplate('set snmp v3 usm local-engine user {user} privacy-aes256 privacy-password {password}',
                                  action_map=ACTION_MAP, error_map=_PRIV_ERROR_MAP)

SET_GROUP = CommandTemplate(
    'set snmp v3 vacm security-to-group security-model usm security-name {user} group {group}',
    action_map=ACTION_MAP, error_map=ERROR_MAP)

CREATE_VIEW = CommandTemplate('set snmp view {view} oid .1 include', action_map=ACTION_MAP,
                              error_map=ERROR_MAP)

SET_ACCESS_NONE_READ = CommandTemplate(
    'set snmp v3 vacm access group {group} default-context-prefix '
    'security-model any security-level none read-view {view}', action_map=ACTION_MAP, error_map=ERROR_MAP)
SET_ACCESS_NONE_WRITE = CommandTemplate(
    'set snmp v3 vacm access group {group} default-context-prefix '
    'security-model any security-level none write-view {view}', action_map=ACTION_MAP, error_map=ERROR_MAP)

SET_ACCESS_AUTH_READ = CommandTemplate(
    'set snmp v3 vacm access group {group} default-context-prefix '
    'security-model any security-level authentication read-view {view}', action_map=ACTION_MAP, error_map=ERROR_MAP)
SET_ACCESS_AUTH_WRITE = CommandTemplate(
    'set snmp v3 vacm access group {group} default-context-prefix '
    'security-model any security-level authentication write-view {view}', action_map=ACTION_MAP, error_map=ERROR_MAP)
SET_ACCESS_PRIV_READ = CommandTemplate(
    'set snmp v3 vacm access group {group} default-context-prefix '
    'security-model any security-level privacy read-view {view}', action_map=ACTION_MAP, error_map=ERROR_MAP)
SET_ACCESS_PRIV_WRITE = CommandTemplate(
    'set snmp v3 vacm access group {group} default-context-prefix '
    'security-model any security-level privacy write-view {view}', action_map=ACTION_MAP, error_map=ERROR_MAP)

DELETE_GROUP_SECURITY = CommandTemplate(
    'delete snmp v3 vacm security-to-group security-model usm security-name {user} group {group}',
    action_map=ACTION_MAP, error_map=ERROR_MAP)
DELETE_GROUP_ACCESS = CommandTemplate('delete snmp v3 vacm access group {group}', action_map=ACTION_MAP,
                                      error_map=ERROR_MAP)
DELETE_VIEW = CommandTemplate('delete snmp view {view}', action_map=ACTION_MAP, error_map=ERROR_MAP)
DELETE_USER = CommandTemplate('delete snmp v3 usm local-engine user {user}', action_map=ACTION_MAP, error_map=ERROR_MAP)
