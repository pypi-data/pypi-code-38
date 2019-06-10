# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import subprocess

def _subprocess_copy(text, args_list):
    p = subprocess.Popen(args_list, stdin=subprocess.PIPE, close_fds=True)
    p.communicate(input=text.encode('utf-8'))


def copy(text, cmd):
    """
    Copy text to OS clipboard.
    """

    # If no command is specified (i.e. the config option is empty) try
    # to find a reasonable default based on the operating system
    if cmd is None:
        if sys.platform == 'darwin':
            cmd = 'pbcopy w'
        else: # For Linux, BSD, cygwin, etc.
            cmd = 'xclip -selection -clipboard'

    _subprocess_copy(text, cmd.split())
