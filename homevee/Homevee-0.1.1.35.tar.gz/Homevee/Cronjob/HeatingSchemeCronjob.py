#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime

from Homevee.Cronjob import IntervalCronjob
from Homevee.Helper import Logger
from Homevee.Manager.ControlManager.ThermostatManager import ThermostatManager
from Homevee.Utils.Database import Database


class HeatingSchemeCronjob(IntervalCronjob):
    def __init__(self):
        super(HeatingSchemeCronjob, self).__init__(task_name="HeatingScheme", interval_seconds=60)

    def task_to_do(self, *args):
        self.run_heating_scheme()

    def run_heating_scheme(self):
        db = Database()

        current_datetime = datetime.datetime.now()

        #Query heating scheme for this day and time
        query = 'SELECT * FROM HEATING_SCHEME, HEATING_SCHEME_DAYS, HEATING_SCHEME_DEVICES WHERE HEATING_SCHEME.ID = HEATING_SCHEME_ID AND HEATING_SCHEME.ID = HEATING_SCHEME_DEVICES.ID AND ACTIVE = "true" AND TIME = :time AND WEEKDAY_ID = :day;'

        current_time = current_datetime.strftime("%H:%M")
        current_day = current_datetime.weekday()

        #Run command
        results = db.select_all(query, {'time': current_time, 'day': current_day})

        for item in results:
            Logger.log(item)

            ThermostatManager().heating_control(None, item['TYPE'], item['DEVICE_ID'], item['VALUE'], db, check_user=False)