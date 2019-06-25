__copyright__ = "# Copyright (c) 2018 by cisco Systems, Inc. All rights reserved."
__author__ = "dwapstra"

from ..settings import IOSXRSettings

class NCS5KSettings(IOSXRSettings):
    def __init__(self):
        super().__init__()

        # prompt wait delay
        self.ESCAPE_CHAR_PROMPT_WAIT = 10

        # prompt wait retries
        self.ESCAPE_CHAR_PROMPT_WAIT_RETRIES = 3
