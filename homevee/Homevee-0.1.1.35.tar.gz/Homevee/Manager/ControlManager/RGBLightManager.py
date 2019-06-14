#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib.error
import urllib.parse
import urllib.request

from Homevee.DeviceAPI import philips_hue
from Homevee.Item.Status import *
from Homevee.Utils.Database import Database
from Homevee.Utils.DeviceTypes import *


class RGBLightManager:
    def __init__(self):
        return

    def rgb_control(self, user, devicetype, id, mode, brightness, color, db, check_user=True):
        if devicetype == URL_RGB_LIGHT:
            result = db.select_one("SELECT * FROM URL_RGB_LIGHT WHERE ID = :id", {'id': id})

            if check_user and not user.has_permission(result['LOCATION']):
                return {'result': 'nopermission'}

            output = urllib.request.urlopen("http://"+result['URL']+color).read()

            return Status(type=STATUS_OK).get_dict()
        elif devicetype == PHILIPS_HUE_LIGHT:
            return philips_hue.set_light_mode(user, id, mode, None, brightness, color, db, check_user=True)

    def get_rgb_devices(self, user, room, db: Database = None):
        if db is None:
            db = Database()
        devices = []

        #URL_RGB_LIGHT
        results = db.select_all("SELECT * FROM URL_RGB_LIGHT WHERE LOCATION = :room", {'room': room})
        for item in results:
            rgb_item = {'name': item['NAME'], 'id': item['ID'], 'type': URL_RGB_LIGHT,
            'icon': item['ICON'], 'value': {'is_on': False, 'brightness': 100, 'color': item['LAST_COLOR']}}
            devices.append(rgb_item)
        #PHILIPS_HUE
        results = db.select_all("SELECT * FROM PHILIPS_HUE_LIGHTS WHERE LOCATION = :room AND TYPE = 'color'", {'room': room})
        for item in results:
            rgb_item = {'name': item['NAME'], 'id': item['ID'], 'type': PHILIPS_HUE_LIGHT,
                        'icon': item['ICON'], 'value': {'is_on': item['IS_ON']== 1, 'brightness': int(item['BRIGHTNESS']/255*100), 'color': item['HUE']}}
            devices.append(rgb_item)

        return devices

    def get_rgb_device(self, user, type, id, db: Database = None):
        if db is None:
            db = Database()

            #URL_RGB_LIGHT
            if type == URL_RGB_LIGHT:
                item = db.select_one("SELECT * FROM URL_RGB_LIGHT WHERE ID = :id", {'id': id})
                rgb_item = {'name': item['NAME'], 'id': item['ID'], 'type': URL_RGB_LIGHT,
                'icon': item['ICON'], 'value': {'is_on': False, 'brightness': 100, 'color': item['LAST_COLOR']}}
                return rgb_item
            #PHILIPS_HUE
            elif type == PHILIPS_HUE_LIGHT:
                item = db.select_one("SELECT * FROM PHILIPS_HUE_LIGHTS WHERE ID = :id AND TYPE = 'color'", {'id': id})

                rgb_item = {'name': item['NAME'], 'id': item['ID'], 'type': PHILIPS_HUE_LIGHT,
                            'icon': item['ICON'], 'value': {'is_on': item['IS_ON']== 1,
                            'brightness': int(item['BRIGHTNESS']/255*100), 'color': item['HUE']}}
                return rgb_item