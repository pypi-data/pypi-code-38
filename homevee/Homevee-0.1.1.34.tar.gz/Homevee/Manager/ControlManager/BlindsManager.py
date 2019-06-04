#!/usr/bin/python
# -*- coding: utf-8 -*-
import traceback

from Homevee.DeviceAPI import rademacher_homepilot
from Homevee.Helper import Logger
from Homevee.Item.Room import Room
from Homevee.Item.Status import *
from Homevee.Utils.Database import Database
from Homevee.Utils.DeviceTypes import *


class BlindsManager:
    def __init__(self):
        return

    def set_blinds(self, user, type, id, new_position, db, check_user=True):
        try:
            if type == RADEMACHER_BLIND_CONTROL:
                data = db.select_one("SELECT LOCATION FROM HOMEPILOT_BLIND_CONTROL WHERE ID = :id", {'id': id})
                if check_user and not user.has_permission(data['LOCATION']):
                    return Status(type=STATUS_NO_PERMISSION).get_dict()

                return rademacher_homepilot.blinds_control.control_blinds(id, new_position)
            else:
                return Status(type=STATUS_NO_SUCH_TYPE).get_dict()
        except:
            if(Logger.IS_DEBUG):
                    traceback.print_exc()
            return Status(type=STATUS_ERROR).get_dict()

    def set_room_blinds(self, user, room, new_position, db: Database = None):
        if db is None:
            db = Database()

            devices = self.get_blinds(user, room)

            for device in devices['blinds']:
                id = device['id']
                type = device['type']
                result = self.set_blinds(user, type, id, new_position, db)
                if 'result' not in result or result['result'] != 'ok':
                    return Status(type=STATUS_ERROR).get_dict()
            return Status(type=STATUS_OK).get_dict()

    def get_all_blinds(self, user, db: Database = None):
        if db is None:
            db = Database()

            rooms = db.select_all("SELECT * FROM ROOMS")
            blinds = []
            for room in rooms:
                if not user.has_permission(room['LOCATION']):
                    continue
                room_blinds = {'name': room['NAME'], 'location': room['LOCATION'], 'icon': room['ICON'],
                                    'blind_array': BlindsManager().get_blinds(user, room['LOCATION'])}
                blinds.append(room_blinds)
            return {'blinds': blinds}

    def get_blinds(self, user, location, db: Database = None):
        if db is None:
            db = Database()
        if not user.has_permission(location):
            return {'result': 'nopermission'}

        if isinstance(location, Room):
            location = location.id

        blinds = []

        #Rademacher HomePilot
        items = db.select_all("SELECT * FROM HOMEPILOT_BLIND_CONTROL WHERE LOCATION = :location",
                    {'location': location})
        for item in items:
            value = int(item['LAST_POS'])

            if value is None:
                value = 0

            blinds.append({'name': item['NAME'], 'id': item['ID'], 'location': location,
                           'icon': item['ICON'], 'value': value, 'type': RADEMACHER_BLIND_CONTROL})

        #Andere Gerätetypen

        return {'blinds': blinds}
