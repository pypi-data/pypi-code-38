# -*- coding: utf-8 -*-

import os

from .trigger import Trigger

HELP = ('@jenkins build <host>:<port> JOB [--parameter <PARAMETER> | -p <PARAMETER>]',
        '@jenkins help',
        '@jenkins list',
        '@jenkins list <host>:<port>',
        '@jenkins query <host>:<port> JOB',
        '@jenkins rebuild <host>:<port> JOB',
        '@jenkins stop <host>:<port> JOB',
        '@jenkins verify <host>:<port> JOB')


class Jenkins(Trigger):
    def __init__(self):
        pass

    def send(self, event):
        if event == 'help':
            return os.linesep.join(HELP), True

        return None, False
