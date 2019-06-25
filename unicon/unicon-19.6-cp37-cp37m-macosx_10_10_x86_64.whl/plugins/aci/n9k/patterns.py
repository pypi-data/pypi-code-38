__copyright__ = "# Copyright (c) 2018 by cisco Systems, Inc. All rights reserved."
__author__ = "dwapstra"

from unicon.plugins.generic.patterns import GenericPatterns

class AciPatterns(GenericPatterns):
    def __init__(self):
        super().__init__()
        self.enable_prompt = r'^(.*?)((%N)|\(none\))#'
        self.loader_prompt = r'^(.*?)loader >\s*$'
