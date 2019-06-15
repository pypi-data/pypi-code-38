# -*- coding: utf-8 -*-

from .trigger import Trigger


class Jenkins(Trigger):
    @staticmethod
    def help():
        return ('Jenkins Trigger'
                ''
                '@jenkins build <host>:<port> JOB [--parameter <PARAMETER> | -p <PARAMETER>]'
                '@jenkins help'
                '@jenkins list'
                '@jenkins list <host>:<port>'
                '@jenkins query <host>:<port> JOB'
                '@jenkins rebuild <host>:<port> JOB'
                '@jenkins stop <host>:<port> JOB'
                '@jenkins verify <host>:<port> JOB')

    def send(self, event):
        return None
