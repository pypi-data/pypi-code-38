#!/usr/bin/python
# # -*- coding: utf-8 -*-
import datetime

from Homevee.Cronjob import FixedTimeCronjob
from Homevee.Helper import Logger
from Homevee.Utils.Database import Database
from Homevee.Utils.DeviceTypes import *


class SaveEnergyDataCronjob(FixedTimeCronjob):
    def __init__(self):
        super(FixedTimeCronjob, self).__init__(task_name="SaveEnergyDataCronjob")

    def task_to_do(self, *args):
        self.save_energy_data()

    def get_seconds_to_wait(self, execution_time=None):
        t = datetime.datetime.today()

        seconds_to_wait = (24 * 60 * 60) - (t.hour * 60 * 60) - (t.minute * 60) - t.second - 60  # um 23:59 ausführen

        return seconds_to_wait

    def save_energy_data(self):
        db = Database()

        date_now = datetime.datetime.now()
        date = date_now.strftime('%Y-%m-%d %H:%M')

        total_value = 0

        room_total_value = {}

        # Z-Wave Stromzähler
        results = db.select_all("SELECT * FROM ZWAVE_POWER_METER")
        for item in results:
            room_id = item['ROOM_ID']
            value = self.save_to_db(date_now, ZWAVE_POWER_METER, room_id, item['DEVICE_ID'],
                               item['VALUE'])
            total_value += value

            if room_id in room_total_value:
                room_total_value[room_id] += value
            else:
                room_total_value[room_id] = value

        #Gesamtwerte der Räume speichern
        for room in room_total_value:
            Logger.log("inserting in room_energy_data of room: "+str(room))
            db.insert("INSERT INTO ROOM_ENERGY_DATA (ROOM_ID, POWER_USAGE, DATE) VALUES (:room, :usage, :date)",
                        {'room': room, 'usage': room_total_value[room_id], 'date': date})

        #Gesamtverbrauch speichern
        Logger.log("inserting in energy_data")
        db.insert("INSERT INTO ENERGY_DATA (DATE, POWER_USAGE) VALUES (:date, :value)",
                    {'date': date, 'value': total_value})

    def save_to_db(self, date_now, type, room_id, id, value, db: Database = None):
        if db is None:
            db = Database()
        if value is None or value == "N/A":
            return

        value = float(value)

        with db:
            date = date_now.strftime('%Y-%m-%d %H:%M')

            if type == ZWAVE_POWER_METER:
                result = db.select_one("SELECT PREV_VALUE FROM ZWAVE_POWER_METER WHERE DEVICE_ID = :id", {'id': id})
                prev_value = float(result['PREV_VALUE'])

                prev_value = prev_value+value
                Logger.log("prev_value: "+str(prev_value))
                Logger.log("updating zwave_power_meter value")
                db.update("UPDATE ZWAVE_POWER_METER SET PREV_VALUE = :val, VALUE = 0 WHERE DEVICE_ID = :id",
                    {'val': prev_value, 'id': id})

            Logger.log("inserting in device_energy_data")
            db.insert("INSERT INTO DEVICE_ENERGY_DATA (LOCATION, DEVICE_ID, DEVICE_TYPE, DATE, POWER_USAGE) \
                            VALUES (:location, :id, :type, :date, :value)",
                        {'location': room_id, 'id': id, 'type': type, 'date': date, 'value': value})

            return value
