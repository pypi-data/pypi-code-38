#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime

from Homevee.Cronjob import FixedTimeCronjob
from Homevee.Item.Device.Sensor.MQTTSensor import MQTTSensor
from Homevee.Item.Device.Sensor.ZWaveSensor import ZWaveSensor
from Homevee.Utils.Database import Database


class SaveSensorDataCronjob(FixedTimeCronjob):
    def __init__(self):
        super(SaveSensorDataCronjob, self).__init__(task_name="SaveSensorDataCronjob")

    def task_to_do(self, *args):
        self.save_sensor_data()

    def get_seconds_to_wait(self, execution_time=None):
        t = datetime.datetime.today()

        seconds_to_wait = (60*60) - (t.minute*60) - t.second

        return seconds_to_wait

    def save_sensor_data(self):
        db = Database()

        sensors = []

        #Z-Wave Sensoren
        sensors.extend(ZWaveSensor.load_all(db))

        #MQTT Sensoren
        sensors.extend(MQTTSensor.load_all(db))

        for sensor in sensors:
            if sensor.save_data:
                self.save_to_db(sensor, db)

    def save_to_db(self, sensor, db: Database = None):
        if db is None:
            db = Database()
        time = datetime.datetime.now().strftime('%Y-%m-%d %H:00')

        db.insert("INSERT INTO SENSOR_DATA (DEVICE_ID, DEVICE_TYPE, DATETIME, VALUE) \
                        VALUES (:id, :type, :time, :value)",
                        {'id': sensor.id, 'type': sensor.get_device_type(), 'time': time, 'value': sensor.value})