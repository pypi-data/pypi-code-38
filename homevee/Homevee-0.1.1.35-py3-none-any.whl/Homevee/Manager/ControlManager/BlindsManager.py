#!/usr/bin/python
# -*- coding: utf-8 -*-

from Homevee.DeviceAPI import rademacher_homepilot
from Homevee.Exception import NoPermissionException, NoSuchTypeException
from Homevee.Item.Room import Room
from Homevee.Utils.Database import Database
from Homevee.Utils.DeviceTypes import *


class BlindsManager:
    def __init__(self):
        return

    def set_blinds(self, user, type, id, new_position, db, check_user=True):
        if type == RADEMACHER_BLIND_CONTROL:
            data = db.select_one("SELECT LOCATION FROM HOMEPILOT_BLIND_CONTROL WHERE ID = :id", {'id': id})
            if check_user and not user.has_permission(data['LOCATION']):
                raise NoPermissionException

            return rademacher_homepilot.blinds_control.control_blinds(id, new_position)
        else:
            raise NoSuchTypeException

    def set_room_blinds(self, user, room, new_position, db: Database = None):
        if db is None:
            db = Database()

            devices = self.get_blinds(user, room)

            for device in devices['blinds']:
                id = device['id']
                type = device['type']
                result = self.set_blinds(user, type, id, new_position, db)
                if 'result' not in result or result['result'] != 'ok':
                    raise Exception

    def get_all_blinds(self, user, db: Database = None):
        if db is None:
            db = Database()

        rooms = db.select_all("SELECT * FROM ROOMS")
        blinds = []
        for room in rooms:
            if not user.has_permission(room['LOCATION']):
                continue

            room_blinds = BlindsManager().get_blinds(user, room['LOCATION'])

            if len(room_blinds) == 0:
                continue

            room_blinds_item = {'name': room['NAME'], 'location': room['LOCATION'], 'icon': room['ICON'],
                                'blind_array': room_blinds}
            blinds.append(room_blinds_item)
        return blinds

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

        return blinds
