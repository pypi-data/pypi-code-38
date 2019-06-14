#!/usr/bin/python
# -*- coding: utf-8 -*-

from Homevee.Cronjob import IntervalCronjob
from Homevee.Utils.Database import Database


class CalendarReminderCronjob(IntervalCronjob):
    def __init__(self):
        super(CalendarReminderCronjob, self).__init__(task_name="CalendarReminder", interval_seconds=60)

    def task_to_do(self, *args):
        self.remind_users()

    def remind_users(self):
        db = Database()
        return