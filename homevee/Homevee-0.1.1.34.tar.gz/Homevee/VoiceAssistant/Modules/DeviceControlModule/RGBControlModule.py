#!/usr/bin/python
# -*- coding: utf-8 -*-
from Homevee.Manager.ControlManager.RGBLightManager import RGBLightManager
from Homevee.Utils.Colors import COLORS, COLOR_NAMES
from Homevee.Utils.Database import Database
from Homevee.Utils.DeviceTypes import *
from Homevee.VoiceAssistant.Modules.DeviceControlModule import VoiceDeviceControlModule


class VoiceRgbDeviceControlModule(VoiceDeviceControlModule):
    def get_pattern(self, db: Database = None):
        if db is None:
            db = Database()
        return [
            [['mach', 'stell', 'tu', 'dreh'], COLORS]
        ]

    def get_label(self):
        return "rgb"

    def run_command(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        return self.voice_rgb_control(username, text, context, db)

    def voice_rgb_control(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        room = self.find_room(text, db)

        if room is not None:
            room_key = room['LOCATION']
        else:
            room_key = None

        device_types = [PHILIPS_HUE_LIGHT, URL_RGB_LIGHT]

        devices = self.find_devices(text, device_types, room_key, db)

        color = self.find_color(text)
        if color != False:
            color_hex = COLOR_NAMES[color]
        else:
            return "Du musst mir eine Farbe sagen."

        for device in devices:
            RGBLightManager().rgb_control(username, device['type'], device['id'], True, None, color_hex, db)

            return {'msg_speech': 'Ok.', 'msg_text': 'Ok.'}

    def find_color(self, text):
        for word in text.split():
            for color in COLORS:
                if word == color:
                    return color
        return False