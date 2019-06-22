# -*- coding: utf-8 -*-

import os

from .trigger import Trigger, TriggerException

HELP = ('@gerrit help',
        '@gerrit list',
        '@gerrit restart <host>',
        '@gerrit start <host>',
        '@gerrit stop <host>',
        '@gerrit verify <host>',
        '@gerrit review <host>:<port>',
        '  [--project <PROJECT> | -p <PROJECT>]',
        '  [--branch <BRANCH> | -b <BRANCH>]',
        '  [--message <MESSAGE> | -m <MESSAGE>]',
        '  [--notify <NOTIFYHANDLING> | -n <NOTIFYHANDLING>]',
        '  [--submit | -s]',
        '  [--abandon | --restore]',
        '  [--rebase]',
        '  [--move <BRANCH>]',
        '  [--publish]',
        '  [--json | -j]',
        '  [--delete]',
        '  [--verified <N>] [--code-review <N>]',
        '  [--label Label-Name=<N>]',
        '  [--tag TAG]',
        '  {COMMIT | CHANGEID,PATCHSET}')


class Gerrit(Trigger):
    def __init__(self, config):
        if config is None:
            raise TriggerException('invalid gerrit configuration')
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
