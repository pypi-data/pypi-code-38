# -*- coding: utf-8 -*-
import datetime


class UpdateTimer(object):
    def __init__(self, interval=1.):
        self.__interval = interval
        self.__start_time = None

    def can_update(self):
        now = datetime.datetime.utcnow()
        if self.__start_time is None or (now - self.__start_time).total_seconds() > self.__interval:
            self.__start_time = now
            return True

        return False
