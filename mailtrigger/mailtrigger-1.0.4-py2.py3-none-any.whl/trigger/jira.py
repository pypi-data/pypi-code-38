# -*- coding: utf-8 -*-

import os

from .trigger import Trigger

HELP = ('TBD',
        '')


class Jira(Trigger):
    def __init__(self):
        pass

    def send(self, event):
        if event == 'help':
            return os.linesep.join(HELP), True

        return None, False
