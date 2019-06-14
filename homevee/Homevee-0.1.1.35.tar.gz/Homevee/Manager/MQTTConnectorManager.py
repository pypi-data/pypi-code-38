#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

from Homevee.Helper.helper_functions import get_my_ip
from Homevee.Item.Status import *
from Homevee.Utils.Database import Database


class MQTTConnectorManager:
    def __init__(self):
        return

    def generate_key(self):
        return "123456"

    def save_mqtt_device(self, user, type, location, id, data, db: Database = None):
        if db is None:
            db = Database()
        if not user.has_permission(location):
            return {'result': 'nopermission'}

        #if type == MQTT_SENSOR:
        #    db.insert("INSERT INTO MQTT_SENSORS")

        item_data = json.loads(data)

        for item in item_data:
            if item['devicetype'] == "sensor":
                db.insert("INSERT INTO MQTT_SENSORS (NAME, ICON, TYPE, ROOM, SAVE_DATA, DEVICE_ID, VALUE_ID, LAST_VALUE) VALUES (:name, :icon, :type, :room, :save_data, :dev_id, :val_id, \"N/A\")",
                {'name': item['name'], 'icon': item['icon'], 'type': item['sensor_type'],
                'room': location, 'save_data': item['save_data'], 'dev_id': id, 'val_id': item['id']})

        return Status(type=STATUS_OK).get_dict()

    def generate_device_data(self, user, location, db: Database = None):
        if db is None:
            db = Database()
        if not user.has_permission(location):
            return {'result': 'nopermission'}

        item = db.select_one("SELECT * FROM MQTT_DEVICES ORDER BY ID DESC", {})

        if item is not None:
            new_id = item['ID']+1
        else:
            new_id = 0

        topic = "/home/device/"+str(new_id)

        key = self.generate_key()

        db.insert("INSERT INTO MQTT_DEVICES (ID, LOCATION, KEY, TOPIC) VALUES (:id, :location, :key, :topic)",
                    {'id': new_id, 'location': location, 'key': key, 'topic': topic})

        return {'id': new_id, 'topic': topic, 'key': key, 'ip': get_my_ip(),
                'remoteid': db.get_server_data("REMOTE_ID")}

    def add_to_intermediates(self, id, db: Database = None):
        if db is None:
            db = Database()
            db.insert("INSERT INTO MQTT_DEVICE_INTERMEDIATES (ID) VALUES (:id)", {'id': id})

    def is_in_intermediates(self, id, db: Database = None):
        if db is None:
            db = Database()
            data = db.select_one("SELECT COUNT(*) FROM MQTT_DEVICE_INTERMEDIATES WHERE ID = :id", {'id': id})

            if data['COUNT(*)'] == 0:
                return False
            else:
                return True
