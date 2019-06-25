""" CSP regex patterns """

__copyright__ = "# Copyright (c) 2017 by cisco Systems, Inc. All rights reserved."
__author__ = "Dave Wapstra <dwapstra@cisco.com>"


from ..patterns import ConfdPatterns

class CspPatterns(ConfdPatterns):
    def __init__(self):
        super().__init__()
        self.cisco_prompt = r'^(.*?)(%N#)\s*$'
        self.cisco_config_prompt = r'^(.*?)(%N\(config.*\)#)\s*$'
        self.cisco_commit_changes_prompt = r'Uncommitted changes found, commit them\? \[yes/no/CANCEL\]'
