# -*- coding: utf-8 -*-

from .trigger import Trigger


class Gerrit(Trigger):
    @staticmethod
    def help():
        return ('Gerrit Trigger'
                ''
                '@gerrit help'
                '@gerrit list'
                '@gerrit restart <host>'
                '@gerrit start <host>'
                '@gerrit stop <host>'
                '@gerrit verify <host>'
                '@gerrit review <host>:<port>'
                '  [--project <PROJECT> | -p <PROJECT>]'
                '  [--branch <BRANCH> | -b <BRANCH>]'
                '  [--message <MESSAGE> | -m <MESSAGE>]'
                '  [--notify <NOTIFYHANDLING> | -n <NOTIFYHANDLING>]'
                '  [--submit | -s]'
                '  [--abandon | --restore]'
                '  [--rebase]'
                '  [--move <BRANCH>]'
                '  [--publish]'
                '  [--json | -j]'
                '  [--delete]'
                '  [--verified <N>] [--code-review <N>]'
                '  [--label Label-Name=<N>]'
                '  [--tag TAG]'
                '  {COMMIT | CHANGEID,PATCHSET}')

    def send(self, event):
        return None
