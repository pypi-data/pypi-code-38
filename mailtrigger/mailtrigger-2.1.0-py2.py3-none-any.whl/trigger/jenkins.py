# -*- coding: utf-8 -*-

import os

from .trigger import Trigger, TriggerException

HELP = ('@jenkins build <host>:<port> JOB [--parameter <PARAMETER> | -p <PARAMETER>]',
        '@jenkins help',
        '@jenkins list',
        '@jenkins list <host>:<port>',
        '@jenkins query <host>:<port> JOB',
        '@jenkins rebuild <host>:<port> JOB',
        '@jenkins stop <host>:<port> JOB',
        '@jenkins verify <host>:<port> JOB')


class Jenkins(Trigger):
    def __init__(self, config):
        if config is None:
            raise TriggerException('invalid jenkins configuration')
        self._debug = config.get('debug', False)
        self._filter = config.get('filter', None)

    def _check(self, event):
        sender = self._filter.get('from', [])
        if event is None or event['from'] not in sender:
            return False
        subject = self._filter.get('subject', None)
        if subject is None or event['subject'].startswith(subject.strip()) is False:
            return False
        return True

    @staticmethod
    def help():
        return os.linesep.join(HELP)

    def run(self, event):
        if self._check(event) is False:
            return '', False
        return '', False
