#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime

from Homevee.Cronjob import IntervalCronjob


class VideoSurveillanceCronjob(IntervalCronjob):
    def __init__(self):
        super(VideoSurveillanceCronjob, self).__init__(task_name="VideoSurveillanceCronjob",
                                                       interval_seconds=15*60)

    def task_to_do(self, *args):
        self.do_video_surveillance()

    def get_seconds_to_wait(self, execution_time=None):
        t = datetime.datetime.today()

        seconds_to_wait = (15 * 60) - ((t.minute * 60) - t.second) % 15 * 60

        return seconds_to_wait

    def do_video_surveillance(self):
        pass