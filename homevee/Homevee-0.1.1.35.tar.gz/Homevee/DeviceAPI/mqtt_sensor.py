#!/usr/bin/python
# -*- coding: utf-8 -*-
from Homevee.Utils.Database import Database


def handle_mqtt_sensor(device_id, value, db: Database = None):
    if db is None:
        db = Database()

    item = db.select_one("SELECT * FROM MQTT_SENSORS WHERE ID = :id", {'id': device_id})

	#if(item['LAST_VALUE'] != value):
		#trigger automation

    db.update("UPDATE MQTT_SENSORS SET LAST_VALUE = :val WHERE ID = :id",
    {'val': value, 'id': device_id})

    #check if device is used in automation rules
