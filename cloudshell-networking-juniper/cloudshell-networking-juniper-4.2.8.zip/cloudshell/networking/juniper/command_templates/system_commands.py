from collections import OrderedDict
from cloudshell.cli.command_template.command_template import CommandTemplate
from cloudshell.networking.juniper.command_templates.generic_action_error_map import ACTION_MAP, ERROR_MAP

_ACTION_MAP = OrderedDict([(r'\[[Yy]es,[Nn]o\]', lambda session, logger: session.send_line('yes', logger))])
_ACTION_MAP.update(ACTION_MAP)

FIRMWARE_UPGRADE = CommandTemplate('request system software add "{src_path}"', action_map=_ACTION_MAP,
                                   error_map=ERROR_MAP)
SHUTDOWN = CommandTemplate('request system power-off', action_map=_ACTION_MAP, error_map=ERROR_MAP)
REBOOT = CommandTemplate('request system reboot', action_map=_ACTION_MAP, error_map=ERROR_MAP)
