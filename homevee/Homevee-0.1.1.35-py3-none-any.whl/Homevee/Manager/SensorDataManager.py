#!/usr/bin/python
# -*- coding: utf-8 -*-
from Homevee.Item import Item
from Homevee.Item.Device import Device
from Homevee.Item.Device.Sensor.MQTTSensor import *
from Homevee.Item.Device.Sensor.ZWaveSensor import *
from Homevee.Item.Room import Room
from Homevee.Item.Status import *
from Homevee.Utils.DeviceTypes import *

SENSOR_TYPE_MAP = {
    'temp': {'name': 'Temperatur', 'einheit': '°C', 'einheit_word': 'Grad'},
    'hygro': {'name': 'Luftfeuchtigkeit', 'einheit': '%', 'einheit_word': '%'},
    'helligkeit': {'name': 'Helligkeit', 'einheit': 'Lux', 'einheit_word': 'Lumen'},
    'uv': {'name': 'UV-Licht', 'einheit': 'UV-Index', 'einheit_word': 'UV-Index'},
    'powermeter': {'name': 'Stromverbrauch', 'einheit': 'Watt', 'einheit_word': 'Watt'},
}


class SensorDataManager:
    def __init__(self):
        return

    def get_einheit(self, type, id, db: Database = None):
        if db is None:
            db = Database()
        db_data = {
            ZWAVE_SENSOR: {'table': 'ZWAVE_SENSOREN', 'sensor_type_col': 'SENSOR_TYPE', 'id_col': 'ID'},
            MQTT_SENSOR: {'table': 'MQTT_SENSORS', 'sensor_type_col': 'TYPE', 'id_col': 'ID'}
        }

        result = db.select_one("SELECT " + db_data[type]['sensor_type_col'] + " FROM " + db_data[type]['table'] + " WHERE " +
                    db_data[type]['id_col'] + " = :id",
                    {'id': id})

        return SENSOR_TYPE_MAP[result[db_data[type]['sensor_type_col']]]['einheit']

    def get_sensor_value(self, type, id, show_einheit, db: Database = None):
        if db is None:
            db = Database()

        module_map = {
            ZWAVE_SENSOR: ZWaveSensor,
            MQTT_SENSOR: MQTT_SENSOR
        }

        if type not in module_map:
            return "N/A"

        sensor = Device.load_from_db(module_map[type], id)
        output = str(sensor.value)
        if show_einheit:
            output += " " + sensor.get_einheit()

        return output


    def get_sensor_data(self, user, room, db: Database = None):
        if db is None:
            db = Database()
        if not user.has_permission(room):
            return Status(type=STATUS_NO_PERMISSION).get_dict()

        values = []

        if isinstance(room, Room):
            rooms = [room]
        elif room is None or room == "all":
            rooms = Room.load_all(db)
        else:
            rooms = [Item.load_from_db(Room, room)]

        for room in rooms:
            value_array = []

            if not user.has_permission(room.id):
                continue

            #TODO weitere Sensortypen hinzufügen
            modules = [ZWaveSensor, MQTTSensor]

            for module in modules:
                devices = Device.get_all(module, room)
                for device in devices:
                    item = device.get_dict()
                    value_array.append(item)

            value_item = {'name': room.name, 'location': room.id, 'icon': room.icon,
                          'value_array': value_array}

            values.append(value_item)

        return values
