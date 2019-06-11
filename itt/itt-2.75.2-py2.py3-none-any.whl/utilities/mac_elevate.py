#!/usr/bin/env python

import os
import sys
import subprocess
import logging_helper


logging = logging_helper.setup_logging(log_to_file=False)


def _mac_elevate(program):

    """Relaunch asking for root privileges."""

    logging.info(u'Relaunching with root permissions')

    applescript = (u'do shell script "{program}" '
                   u'with administrator privileges'.format(program=program))

    subprocess.call([u'osascript', u'-s', u'o', u'-e', applescript])


def elevate(program):

    """Elevate user permissions if needed"""

    if sys.platform == u'darwin':
        try:
            os.setuid(0)
        except OSError:
            _mac_elevate(program)
