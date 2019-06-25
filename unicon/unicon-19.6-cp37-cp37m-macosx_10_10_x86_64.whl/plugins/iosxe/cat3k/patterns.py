__copyright__ = "# Copyright (c) 2016 by cisco Systems, Inc. All rights reserved."
__author__ = "Giacomo Trifilo <gtrifilo@cisco.com>"

from unicon.plugins.iosxe.patterns import IosXEPatterns


class IosXECat3kPatterns(IosXEPatterns):
    def __init__(self):
        super().__init__()
        self.rommon_prompt = r'(.*)switch:\s?$'
        self.tcpdump = ".*listening on lfts.*$"
