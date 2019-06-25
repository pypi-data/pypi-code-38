__copyright__ = "# Copyright (c) 2016 by cisco Systems, Inc. All rights reserved."
__author__ = "Myles Dear <mdear@cisco.com>"

from .patterns import IosvPatterns
from unicon.eal.dialogs import Statement

patterns = IosvPatterns()

dest_file_startup = Statement(pattern=patterns.dest_file_startup,
    action="sendline()",
    loop_continue=True,
    continue_timer=False)

