""" Defines the settings for uc based unicon connections """

__copyright__ = "# Copyright (c) 2017 by cisco Systems, Inc. All rights reserved."
__author__ = "Dave Wapstra <dwapstra@cisco.com>"

from unicon.plugins.generic.settings import GenericSettings


class VosSettings(GenericSettings):
    """" Generic platform settings """
    def __init__(self):
        """ initialize
        """
        super().__init__()
        self.HA_INIT_EXEC_COMMANDS = [
            'set cli pagination off'
        ]
        self.HA_INIT_CONFIG_COMMANDS = []
