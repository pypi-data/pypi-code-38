#!/usr/bin/python
# -*- coding: utf-8 -*-
from Homevee.Manager import SensorDataManager
from Homevee.Manager.SensorDataManager import SENSOR_TYPE_MAP
from Homevee.Utils.Database import Database
from Homevee.Utils.DeviceTypes import *
from Homevee.VoiceAssistant import Helper
from Homevee.VoiceAssistant.Modules.DeviceControlModule import VoiceDeviceControlModule


class VoiceDeviceGetSensorDataModule(VoiceDeviceControlModule):
    def get_pattern(self, db: Database = None):
        if db is None:
            db = Database()
        SENSOR_ADJECTIVES = ['warm', 'kalt', 'dunkel', 'hell', 'feucht', 'laut']
        SENSOR_SUBJECTIVES = ['temperatur', 'helligkeit', 'luftfeuchtigkeit', 'lautstärke', 'verbrauch',
                              'stromverbrauch']
        return [
            ['wie', SENSOR_ADJECTIVES, 'ist'],
            ['wie', 'ist', ['der', 'die', 'das'], SENSOR_SUBJECTIVES]
        ]

    def get_label(self):
        return "sensor"

    def run_command(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        return self.get_sensor_data(username, text, context, db)

    def get_context_key(self):
        return "CONTEXT_GET_SENSOR_DATA"

    def get_sensor_data(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        room = self.find_room(text, db)

        sensor_type = self.find_sensor_type(text)

        if sensor_type is None:
            if context is not None and context:
                sensor_type = context['sensor_type']

        if room is None:
            if context is None:
                answer_data = [
                    ['Welchen Raum ', ['meinst du', 'möchtest du abfragen'], '?']
                ]
                output = Helper.generate_string(answer_data)

                Helper.set_context(username, self.get_context_key(), {'sensor_type': sensor_type}, db)

                return {'msg_speech': output, 'msg_text': output}
            else:
                if 'room' in context:
                    room = context['room']
                    #print(room)

        if sensor_type in SENSOR_TYPE_MAP:
            einheit = SENSOR_TYPE_MAP[sensor_type]['einheit_word']
        else:
            answer_data = [
                ['Diesen Wert kann ich noch nicht abfragen.'],
                ['Dieser Wert kann noch nicht abgefragt werden.']
            ]
            output = Helper.generate_string(answer_data)
            return {'msg_speech': output, 'msg_text': output}


        values = []



        data = [
            {'type': ZWAVE_SENSOR, 'table': 'ZWAVE_SENSOREN', 'id_col': 'ID', 'room_col': 'RAUM', 'type_col': 'SENSOR_TYPE'},
            {'type': MQTT_SENSOR, 'table': 'MQTT_SENSORS', 'id_col': 'ID', 'room_col': 'ROOM', 'type_col': 'TYPE'}
        ]

        for item in data:
            results = db.select_all("SELECT * FROM "+item['table']+" WHERE "+item['type_col']+" = :type AND "+item['room_col']+" = :room",
                        {'type': sensor_type, 'room': room['LOCATION']})

            for sensor in results:
                values.append(SensorDataManager.get_sensor_value(item['type'], sensor[item['id_col']], False, db))

        if len(values) > 0:
            #compute average value of all sensors in this room
            sum = 0

            try:
                for value in values:
                    sum += float(value)
            except Exception:
                answer_data = [
                    ['Im Raum ' + room['NAME'], ' gibt es noch keine ', ['Messungen', 'Werte', 'Sensorwerte'],'.']
                ]

                output = Helper.generate_string(answer_data)

                return {'msg_speech': output, 'msg_text': output}

            if sensor_type not in ['powermeter']:
                avg_value = sum/len(values)
                value_word = str(avg_value) + ' ' + einheit
                answer_data = [
                    ['Im Raum ' + room['NAME'], ' hat es ' + value_word, '.']
                ]
            else:
                value_word = str(int(sum)) + ' ' + einheit
                answer_data = [
                    ['Im Raum ' + room['NAME'], ' liegt der  ', ['Verbrauch', 'Stromverbrauch'],' bei ', value_word, '.'],
                    ['Der Raum ' + room['NAME'], ' verbraucht aktuell  ', value_word, '.']
                ]

            output = Helper.generate_string(answer_data)

            # helper.set_context(username, GET_SENSOR_DATA, {'room': room}, db)
        else:
            answer_data = [
                ['Ich konnte ', ['hier', 'in diesem Raum'] ,' keine ', ['Daten', 'Sensoren', 'Sensorwerte'], ' finden.']
            ]
            output = Helper.generate_string(answer_data)

        return {'msg_speech': output, 'msg_text': output}

    def get_reed_data(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        room = self.find_room(text, db)

        output = 'Reed'
        return {'msg_speech': output, 'msg_text': output}

    def get_presence_data(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        room = self.find_room(text, db)

        output = 'Anwesenheit'
        return {'msg_speech': output, 'msg_text': output}

    def find_sensor_type(self, text):
        words = text.split()

        type_keywords = [
            {'type': 'temp', 'items': ['warm', 'kalt', 'temperatur']},
            {'type': 'hygro', 'items': ['feucht', 'luftfeuchtigkeit', 'luftfeuchte']},
            {'type': 'helligkeit', 'items': ['hell', 'helligkeit']},
            {'type': 'uv', 'items': ['uv-licht']},
            {'type': 'powermeter', 'items': ['verbrauch', 'stromverbrauch']}
        ]

        for type_keyword in type_keywords:
            for keyword in type_keyword['items']:
                if keyword in words:
                    return type_keyword['type']

        return None