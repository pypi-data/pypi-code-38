""" ConfdD regex patterns """

__copyright__ = "# Copyright (c) 2017 by cisco Systems, Inc. All rights reserved."
__author__ = "Dave Wapstra <dwapstra@cisco.com>"


from unicon.plugins.generic.patterns import GenericPatterns

class ConfdPatterns(GenericPatterns):
    def __init__(self):
        super().__init__()
        self.cisco_prompt = r'^(.*?)([-\.\w]+@[-\.\w]+#)\s*$'
        self.juniper_prompt = r'^(.*?)([-\.\w]+@[-\.\w]+>)\s*$'
        self.cisco_or_juniper_prompt = r'^(.*)([-\.\w]+@[-\.\w]+[#>])\s*$'
        self.cisco_config_prompt = r'^(.*?)([-\.\w]+@[-\.\w]+\(config.*\)#)\s*$'
        self.juniper_config_prompt = r'^(.*?)((\[edit\]\r\n)?[-\.\w]+@[-\.\w]+%)\s*$'
        self.cisco_or_juniper_config_prompt = r'^(.*?)((\[edit\]\r\n)?[-\.\w]+@[-\.\w]+(\(config.*\)#|%))\s*$'
        self.connected_console = r"^(.*?)connected from .* using console"
