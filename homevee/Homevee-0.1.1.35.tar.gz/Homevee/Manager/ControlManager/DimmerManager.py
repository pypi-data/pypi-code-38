#!/usr/bin/python
# -*- coding: utf-8 -*-
from Homevee.DeviceAPI import zwave
from Homevee.Exception import NoSuchTypeException, NoPermissionException
from Homevee.Item.Status import *
from Homevee.Utils.Database import Database
from Homevee.Utils.DeviceTypes import *

class DimmerManager:
    def __init__(self):
        return

    def get_dimmers(self, user, room, db: Database = None):
        if db is None:
            db = Database()
        if not user.has_permission(room):
            return Status(type=STATUS_NO_PERMISSION).get_dict()

        dimmer = []
        #Z-Wave Dimmer
        results = db.select_all("SELECT * FROM ZWAVE_DIMMER WHERE LOCATION == :room", {'room': room})

        for item in results:
            dimmer_item = {'device': item['ID'], 'value': item['VALUE'], 'icon': item['ICON'],
                         'name': item['NAME'], 'type': ZWAVE_DIMMER}
            dimmer.append(dimmer_item)

        return dimmer

    def set_dimmer(self, user, type, id, value, db: Database = None):
        if db is None:
            db = Database()
        if type == ZWAVE_DIMMER:
            return self.set_zwave_dimmer(user, id, value, db)
        else:
            raise NoSuchTypeException

    def set_zwave_dimmer(self, user, id, value, db: Database = None):
        if db is None:
            db = Database()

            data = db.select_one("SELECT * FROM ZWAVE_DIMMER WHERE ID == :device",
                        {'device': id})

            if not user.has_permission(data['LOCATION']):
                raise NoPermissionException

            device_id = data['ID']

            result = zwave.device_control.set_multistate_device(device_id, value, db)

            if result['code'] == 200:
                db.update("UPDATE ZWAVE_DIMMER SET VALUE = :value WHERE ID = :id",
                            {'value': value, 'id': id})
            else:
                raise Exception