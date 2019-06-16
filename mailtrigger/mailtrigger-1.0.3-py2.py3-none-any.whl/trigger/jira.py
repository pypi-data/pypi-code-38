# -*- coding: utf-8 -*-

from .trigger import Trigger


class Jira(Trigger):
    @staticmethod
    def help():
        return ('Jira Trigger'
                ''
                'TBD')

    def send(self, event):
        return None
