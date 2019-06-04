#!/usr/bin/python
# -*- coding: utf-8 -*-
from Homevee.DeviceAPI import philips_hue
from Homevee.DeviceAPI.set_modes import set_modes
from Homevee.Manager.ControlManager import BlindsManager
from Homevee.Manager.ControlManager.ThermostatManager import ThermostatManager
from Homevee.Utils.Database import Database
from Homevee.Utils.DeviceTypes import *
from Homevee.VoiceAssistant.Helper import generate_string, set_context, get_okay
from Homevee.VoiceAssistant.Modules.DeviceControlModule import VoiceDeviceControlModule

CONTEXT_SET_MODES = "CONTEXT_SET_MODES"
CONTEXT_SET_HEATING = "CONTEXT_SET_HEATING"
CONTEXT_SET_THERMOSTAT = "CONTEXT_SET_THERMOSTAT"
CONTEXT_CONTROL_BLINDS = "CONTEXT_CONTROL_BLINDS"

class VoiceDeviceSetModesModule(VoiceDeviceControlModule):
    def get_pattern(self, db: Database = None):
        if db is None:
            db = Database()
        data = [
            ['FUNKSTECKDOSEN', 'NAME', 'DEVICE', FUNKSTECKDOSE],
            ['ZWAVE_SWITCHES', 'NAME', 'ID', ZWAVE_SWITCH],
            ['URL_SWITCH_BINARY', 'NAME', 'ID', URL_SWITCH],
            ['URL_TOGGLE', 'NAME', 'ID', URL_TOGGLE],
            ['PHILIPS_HUE_LIGHTS', 'NAME', 'ID', PHILIPS_HUE_LIGHT],
            ['URL_RGB_LIGHT', 'NAME', 'ID', URL_RGB_LIGHT]
        ]
        device_names = []
        for item in data:
            results = db.select_all("SELECT * FROM " + item[0], {})
            for device in results:
                device_names.append(device[item[1]].lower())
        output_array = [
            [['mach', 'schalt'], device_names, ['an', 'ein', 'aus']],
            [device_names, ['an', 'ein', 'aus']]
        ]
        # print output_array
        return output_array

    def get_label(self):
        return "switch"

    def get_context_key(self):
        return [
            CONTEXT_SET_THERMOSTAT,
            CONTEXT_CONTROL_BLINDS,
            CONTEXT_SET_HEATING,
            CONTEXT_SET_MODES
        ]

    def run_command(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        return self.set_modes_voice(username, text, context, db)

    def set_modes_voice(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        room = self.find_room(text, db)

        if room is not None:
            room_key = room['LOCATION']
        else:
            room_key = None

        device_types = [FUNKSTECKDOSE, ZWAVE_SWITCH, URL_SWITCH, URL_TOGGLE, PHILIPS_HUE_LIGHT, URL_RGB_LIGHT]

        devices = self.find_devices(text, device_types, room_key, db)

        if len(devices) == 0:
            #Keine Geräte gefunden
            answer_data = [
                [['Dieses ', 'Das genannte '], 'Gerät ', ['existiert nicht.', 'gibt es nicht.', 'wurde noch nicht angelegt.']]
            ]

            answer = generate_string(answer_data)

            return {'msg_speech': answer, 'msg_text': answer}

        words = text.split(" ")
        mode = None
        on_words = ['an', 'ein']
        off_words = ['aus']
        for word in words:
            if word in on_words:
                mode = 1
                break
            elif word in off_words:
                mode = 0
                break

        if mode is None:
            if 'mode' in context:
                mode = context['mode']
            else:
                # Kein Zustand angegeben
                answer_data = [
                    ['Soll ', 'ich ', 'die Geräte ', ['an', 'ein'], '- oder aus', ['schalten', 'machen'], [', '+username, ''], '?']
                ]

                answer = generate_string(answer_data)

                return {'msg_speech': answer, 'msg_text': answer}

        #Geräte schalten
        for device in devices:
            if(device['type'] == PHILIPS_HUE_LIGHT):
                philips_hue.set_light_mode(username, device['id'], mode, None, None, None, db)
            else:
                set_modes(username, device['type'], device['id'], mode, db)

        set_context(username, CONTEXT_SET_MODES, {'location': room, 'devices': devices, 'mode':mode}, db)

        MODE_WORDS = on_words
        if mode == 0:
            MODE_WORDS = off_words

        DEVICE_STRING = None
        if len(devices) > 1:
            VERB = "wurden"
            DEVICE_WORD = "Die Geräte "

            for i in range(0, len(devices)):
                if DEVICE_STRING is None:
                    DEVICE_STRING = '' + devices[i]['name'] + ''
                elif i == len(devices) - 1:
                    DEVICE_STRING = DEVICE_STRING + ' und ' + '' + devices[i]['name'] + ''
                else:
                    DEVICE_STRING = DEVICE_STRING + ', ' + '' + devices[i]['name'] + ''

        else:
            DEVICE_WORD = "Das Gerät "
            VERB = "wurde"

            DEVICE_STRING = '' + devices[0]['name'] + ''

        answer_data = [
            [get_okay(), [', ' + username, ''], '.',
             ['', [' ', DEVICE_WORD,  [DEVICE_STRING + ' ', ''], VERB + ' ',
                   MODE_WORDS, ['geschaltet', 'geschalten'], '.']]]
        ]

        answer = generate_string(answer_data)

        return {'msg_speech': answer, 'msg_text': answer}

    def control_blinds(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        words = text.split(" ")

        value = None

        if context is not None:
            if 'value' in context:
                value = int(context['value'])

        if value is None:
            if 'auf' not in words or len(words) <= words.index('auf') + 1:
                close_words = ['zu', 'runter', 'herunter']
                open_words = ['auf', 'rauf', 'hoch']

                for word in words:
                    if word in close_words:
                        value = 100
                        break
                    elif word in open_words:
                        value = 0
                        break
            else:
                value = words[words.index('auf') + 1]

        room = self.find_room(text, db)
        if room is not None:
            room_key = room['LOCATION']
        else:
            if context is not None and 'room' in context and context['room'] is not None:
                room = context['room']
                room_key = context['room']['LOCATION']
            else:
                # no room => control in every room
                room = None
                '''
                answer_data = [
                    [['Wo ', 'In welchem Raum '], 'soll ich das machen', [', ' + username, ''], '?']
                ]
    
                if value is not None:
                    set_context(username, CONTROL_BLINDS, {'value': value}, db)
    
                answer = generate_string(answer_data)
    
                return {'msg_speech': answer, 'msg_text': answer}
                '''

        #print(str(room) + ": " + str(value))

        blinds = []

        blinds_db_data = [
            {'table': 'HOMEPILOT_BLIND_CONTROL', 'room_col': 'LOCATION', 'id_col': 'ID', 'type': RADEMACHER_BLIND_CONTROL}
        ]

        for data_item in blinds_db_data:
            if room is not None:
                results = db.select_all('SELECT * FROM ' + data_item['table'] + ' WHERE ' + data_item['room_col'] + ' = :room',
                        {'room': room_key})
            else:
                results = db.select_all('SELECT * FROM ' + data_item['table'], db)

            for item in results:
                blinds_item = {'type': data_item['type'], 'id': item[data_item['id_col']]}
                blinds.append(blinds_item)

        #print(blinds)

        for blinds_item in blinds:
            BlindsManager.set_blinds(username, blinds_item['type'], blinds_item['id'], value, db)

        # set_context(username, SET_THERMOSTAT, {'room': room, 'value': value}, db)

        bezeichner = ['Der Rollladen wurde', 'Die Rolläden wurden', 'Die Jalousien wurden']

        if room is None:
            bezeichner = ['Alle Rolläden wurden', 'Alle Jalousien wurden', 'Jeder Rollladen wurde']

        opened_words = ['geöffnet', 'hochgefahren']
        closed_words = ['geschlossen', 'runtergefahren']

        value_string = ['auf '+str(value)+' % ', ['gefahren', 'eingestellt']]

        if value is 0:
            action_string = opened_words
        elif value is 100:
            action_string = closed_words
        else:
            action_string = value_string

        answer_data = [
            [get_okay(), [', ' + username, ''], '.',
             ['', [' ', bezeichner, ' ', action_string, '.']]]
        ]

        answer = generate_string(answer_data)

        return {'msg_speech': answer, 'msg_text': answer}

    def set_thermostat(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        words = text.split(" ")

        if 'auf' not in words or len(words) < words.index('auf')+1:
            if context is not None and 'value' in context and context['value'] is not None:
                value = context['value']
            else:
                answer_data = [
                    [['Welchen Wert ', 'Welche Temperatur'], ' soll ich einstellen', [', ' + username, ''], '?']
                ]

                set_context(username, CONTEXT_SET_THERMOSTAT, context, db)

                answer = generate_string(answer_data)

                return {'msg_speech': answer, 'msg_text': answer}
        else:
            value = words[words.index('auf')+1]

        room = self.find_room(text, db)
        if room is not None:
            room_key = room['LOCATION']
        else:
            if context is not None and 'room' in context and context['room'] is not None:
                room = context['room']
                room_key = context['room']['LOCATION']
            else:
                # no room
                answer_data = [
                    [['Wo ', 'In welchem Raum '], 'soll ich das machen', [', ' + username, ''], '?']
                ]

                if value is not None:
                    set_context(username, CONTEXT_SET_THERMOSTAT, {'value': value}, db)

                answer = generate_string(answer_data)

                return {'msg_speech': answer, 'msg_text': answer}

        #print(str(room)+": "+value)

        thermostats = []

        thermostat_db_data = [
            {'table': 'MAX_THERMOSTATS', 'room_col': 'RAUM', 'id_col': 'ID', 'type': MAX_THERMOSTAT},
            {'table': 'ZWAVE_THERMOSTATS', 'room_col': 'RAUM', 'id_col': 'THERMOSTAT_ID', 'type': ZWAVE_THERMOSTAT}
        ]

        for data_item in thermostat_db_data:
            results = db.select_all('SELECT * FROM '+data_item['table']+' WHERE '+data_item['room_col']+' = :room',
                        {'room': room_key})

            for item in results:
                thermostat = {'type': data_item['type'], 'id': item[data_item['id_col']]}
                thermostats.append(thermostat)

        #print(thermostats)

        for thermostat in thermostats:
            ThermostatManager().heating_control(username, thermostat['type'], thermostat['id'], value, db)

        #set_context(username, SET_THERMOSTAT, {'room': room, 'value': value}, db)

        answer_data = [
            [get_okay(), [', '+username, ''], '.',
             ['', [' ', ['Die Heizung', 'Das Thermostat', 'Die Temperatur'], ' wurde ',
              ['', ['auf '+ value + ' Grad ']],
              ['angepasst', 'neu eingestellt', 'geändert'], '.']]]
        ]

        answer = generate_string(answer_data)

        return {'msg_speech': answer, 'msg_text': answer}

    def set_dimmer(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        room = self.find_room(text, db)

        if room is not None:
            room_key = room['LOCATION']
        else:
            room_key = None

        device_types = [FUNKSTECKDOSE, ZWAVE_SWITCH, URL_SWITCH, URL_TOGGLE, PHILIPS_HUE_LIGHT, URL_RGB_LIGHT]

        devices = self.find_devices(text, device_types, room_key, db)
        return {'msg_speech':"Ok", 'msg_text':"Dimmer"}