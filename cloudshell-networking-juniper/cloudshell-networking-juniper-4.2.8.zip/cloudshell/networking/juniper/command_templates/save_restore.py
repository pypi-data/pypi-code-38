from collections import OrderedDict
from cloudshell.cli.command_template.command_template import CommandTemplate
from cloudshell.networking.juniper.command_templates.generic_action_error_map import ACTION_MAP, ERROR_MAP

_ERROR_MAP = OrderedDict(
    [(r'[Ee]rror\ssaving\sconfiguration', 'Error saving configuration')])
_ERROR_MAP.update(ERROR_MAP)

SAVE = CommandTemplate('save "{dst_path}"', action_map=ACTION_MAP, error_map=_ERROR_MAP)
RESTORE = CommandTemplate('load {restore_type} "{src_path}"', action_map=ACTION_MAP, error_map=_ERROR_MAP)
