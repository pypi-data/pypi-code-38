#!/usr/bin/python
# -*- coding: utf-8 -*-

from Homevee.Cronjob import IntervalCronjob
from Homevee.DeviceAPI import philips_hue
from Homevee.Utils.Database import Database


class PhilipsHueValueLoaderCronjob(IntervalCronjob):
    def __init__(self):
        super(PhilipsHueValueLoaderCronjob, self).__init__(task_name="PhilipsHueValueLoaderCronjob", interval_seconds=5*60)

    def task_to_do(self, *args):
        self.load_hue_values()

    def load_hue_values(self):
        db = Database()

        results = db.select_all("SELECT * FROM PHILIPS_HUE_LIGHTS", {})
        for item in results:
            counter = 3
            for i in range(0, counter):
                if(philips_hue.get_light_info(item['ID'], db)):
                    break