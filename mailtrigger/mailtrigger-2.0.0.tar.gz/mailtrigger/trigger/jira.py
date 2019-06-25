# -*- coding: utf-8 -*-

from .trigger import Trigger, TriggerException


class Jira(Trigger):
    def __init__(self, config):
        if config is None:
            raise TriggerException('invalid jira configuration')
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
        return ''

    def run(self, event):
        if self._check(event) is False:
            return '', False
        return '', False
