# -*- coding: utf-8 -*-

import os

from .trigger import Trigger, TriggerException
from ..registry import REGISTRY


class Helper(Trigger):
    def __init__(self, config):
        if config is None:
            raise TriggerException('invalid helper configuration')
        self._debug = config.get('debug', False)
        self._filter = config.get('filter', None)
        self._trigger = '@help'

    def _check(self, event):
        sender = self._filter.get('from', [])
        if event is None or event['from'] not in sender:
            return False
        subject = self._filter.get('subject', None)
        if subject is None or event['subject'].startswith(subject.strip()) is False:
            return False
        return True

    def _parse(self, event):
        lines = event['content'].splitlines()
        ret = False
        for item in lines:
            if self._trigger == item.strip():
                ret = True
                break
        return ret

    @staticmethod
    def help():
        return ''

    def run(self, event):
        if self._check(event) is False:
            return '', False
        if self._parse(event) is False:
            return '', False
        msg = []
        for item in REGISTRY:
            msg.append(item['class'].help())
        return os.linesep.join(msg), True
