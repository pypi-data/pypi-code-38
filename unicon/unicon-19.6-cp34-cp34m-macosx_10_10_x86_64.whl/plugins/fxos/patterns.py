__copyright__ = "# Copyright (c) 2017 by cisco Systems, Inc. All rights reserved."
__author__ = "dwapstra"

from unicon.plugins.generic.patterns import GenericPatterns

class FxosPatterns(GenericPatterns):
    def __init__(self):
        super().__init__()
        self.shell_prompt = r'^(.*?([>\$~%]|(/[-\w]+)*\*?[^#]+#))\s?$'
