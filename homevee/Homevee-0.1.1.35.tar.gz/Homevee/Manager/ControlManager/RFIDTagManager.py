#!/usr/bin/python
# -*- coding: utf-8 -*-
from Homevee.DeviceAPI.get_modes import get_modes
from Homevee.DeviceAPI.set_modes import set_modes
from Homevee.Helper import Logger
from Homevee.Item.Status import *
from Homevee.Manager.ControlManager.WakeOnLanManager import WakeOnLanManager
from Homevee.Manager.DashboardManager import DashboardManager
from Homevee.Utils.Database import Database
from Homevee.Utils.DeviceTypes import *


class RFIDTagManager:
    def __init__(self):
        return

    def get_rfid_tags(self, user, db: Database = None):
        if db is None:
            db = Database()

        results = db.select_all("SELECT * FROM RFID_TAGS")

        tags = []

        for item in results:
            try:
                device_info = DashboardManager().get_device_info(user, item['ACTION_TYPE'], item['ACTION_ID'], db)

                Logger.log(item)
                Logger.log(device_info)

                tag = {'name': item['NAME'], 'uuid': item['UUID'], 'actiontype': item['ACTION_TYPE'],
                       'actionid': item['ACTION_ID'], 'roomname': device_info['roomname'], 'actionname': device_info['name']}
                tags.append(tag)
            except:
                continue

        return tags

    def add_edit_rfid_tag(self, user, name, uuid, actionType, actionId, db: Database = None):
        if db is None:
            db = Database()

        result = db.select_one("SELECT COUNT(*) FROM RFID_TAGS WHERE UUID = :uuid", {'uuid': uuid})

        is_new = result['COUNT(*)'] is not 1

        param_array = {'name': name, 'uuid': uuid, 'type': actionType, 'id': actionId}

        if is_new:
            db.insert("INSERT INTO RFID_TAGS (NAME, UUID, ACTION_TYPE, ACTION_ID) VALUES (:name, :uuid, :type, :id)",
                        param_array)
        else:
            db.update("UPDATE RFID_TAGS SET NAME = :name, ACTION_TYPE = :type, ACTION_ID = :id WHERE UUID = :uuid",
                        param_array)

        return Status(type=STATUS_OK).get_dict()

    def delete_rfid_tag(self, user, uuid, db: Database = None):
        if db is None:
            db = Database()

        db.delete("DELETE FROM RFID_TAGS WHERE UUID = :uuid", {'uuid': uuid})

        return Status(type=STATUS_OK).get_dict()


    def wake_xbob_on_lan(self, user, id, db: Database = None):
        if db is None:
            db = Database()
        pass


    def run_rfid_action(self, user, uuid, db: Database = None):
        if db is None:
            db = Database()
        result = db.select_one("SELECT * FROM RFID_TAGS WHERE UUID = :uuid", {'uuid': uuid})

        if result is None:
            return {'result': 'tagnotfound'}
        else:
            type = result['ACTION_TYPE']
            id = result['ACTION_ID']

            if type in [FUNKSTECKDOSE, ZWAVE_SWITCH, URL_SWITCH, URL_TOGGLE]:
                mode = get_modes(user, None, type, id, db)

                if mode == "1" or mode == 1 or mode == True or mode == "true":
                    mode = 0
                else:
                    mode = 1

                result = set_modes(user, type, id, mode, db)

            elif type == WAKE_ON_LAN:
                result = WakeOnLanManager().wake_on_lan(user, id, db)

            elif type == XBOX_ONE_WOL:
                result = self.wake_xbob_on_lan(user, id, db)

        return Status(type=STATUS_OK).get_dict()