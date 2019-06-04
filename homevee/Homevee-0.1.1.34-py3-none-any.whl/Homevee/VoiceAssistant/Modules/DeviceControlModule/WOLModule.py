#!/usr/bin/python
# -*- coding: utf-8 -*-
from Homevee.Helper import Logger
from Homevee.Manager.ControlManager.WakeOnLanManager import WakeOnLanManager
from Homevee.Utils.Database import Database
from Homevee.Utils.DeviceTypes import *
from Homevee.VoiceAssistant.Helper import generate_string, set_context, get_okay
from Homevee.VoiceAssistant.Modules.DeviceControlModule import VoiceDeviceControlModule


class VoiceDeviceWakeOnLanModule(VoiceDeviceControlModule):
    def get_context_key(self):
        return "VOICE_WAKE_ON_LAN"

    def get_pattern(self, db: Database = None):
        if db is None:
            db = Database()
        data = [
            ['WAKE_ON_LAN', 'NAME', 'DEVICE', WAKE_ON_LAN],
            ['XBOX_ONE_WOL', 'NAME', 'ID', XBOX_ONE_WOL]
        ]
        device_names = []
        for item in data:
            results = db.select_all("SELECT * FROM " + item[0], {})
            for device in results:
                device_names.append(device[item[1]].lower())
        output_array = [
            [['fahr'], device_names, ['hoch']]
        ]
        return output_array

    def get_label(self):
        return "wakeonlan"

    def voice_wol(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        room = self.find_room(text, db)

        if room is not None:
            room_key = room['LOCATION']
        else:
            room_key = None

        device_types = [WAKE_ON_LAN, XBOX_ONE_WOL]

        devices = self.find_devices(text, device_types, room_key, db)

        if len(devices) == 0:
            #Keine Geräte gefunden
            answer_data = [
                [['Dieses ', 'Das genannte '], 'Gerät ', ['existiert nicht.', 'gibt es nicht.', 'wurde noch nicht angelegt.']]
            ]

            answer = generate_string(answer_data)

            return {'msg_speech': answer, 'msg_text': answer}

        words = text.split(" ")

        #Geräte schalten
        for device in devices:
            if device['type'] == XBOX_ONE_WOL:
                Logger.log("")
                #xbox_wake_up(username, device['id'], db)
            else:
                WakeOnLanManager().wake_on_lan(username, device['id'], db)

        set_context(username, self.get_context_key(), {'location': room, 'devices': devices}, db)

        DEVICE_STRING = None
        if len(devices) > 1:
            VERB = "wurden"
            DEVICE_WORD = "Die Geräte "

            for i in range(0, len(devices)):
                if DEVICE_STRING is None:
                    DEVICE_STRING = '\'' + devices[i]['name'] + '\''
                elif i == len(devices) - 1:
                    DEVICE_STRING = DEVICE_STRING + ' und ' + '\'' + devices[i]['name'] + '\''
                else:
                    DEVICE_STRING = DEVICE_STRING + ', ' + '\'' + devices[i]['name'] + '\''
        else:
            DEVICE_WORD = "Das Gerät "
            VERB = "wurde"

            DEVICE_STRING = '\'' + devices[0]['name'] + '\''

        answer_data = [
            [get_okay(), [', ' + username, ''], '.',
             ['', [' ', DEVICE_WORD,  [DEVICE_STRING + ' ', ''], VERB + ' ',
                   ['gestartet', 'eingeschalten', 'eingeschaltet', 'an gemacht', 'hochgefahren'], '.']]]
        ]

        answer = generate_string(answer_data)

        return {'msg_speech': answer, 'msg_text': answer}