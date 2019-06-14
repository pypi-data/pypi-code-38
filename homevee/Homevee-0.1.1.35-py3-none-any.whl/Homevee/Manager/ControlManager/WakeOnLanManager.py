import os

from Homevee.DeviceAPI.XBOXOneAPI import XBOXOneAPI
from Homevee.Item.Status import *
from Homevee.Utils.Database import Database


class WakeOnLanManager:
    def __init__(self):
        return

    def wake_on_lan(self, user, id, db, check_user=True):
        device = db.select_all("SELECT * FROM WAKE_ON_LAN WHERE DEVICE == :id", {'id': id})
        if check_user and not user.has_permission(device['LOCATION']):
            return {'result': 'nopermission'}

        os.system("sudo wakeonlan "+device['MAC_ADDRESS'])

    def get_wol_devices(self, user, room, db: Database = None):
        if db is None:
            db = Database()
        if not user.has_permission(room):
            return Status(type=STATUS_NO_PERMISSION).get_dict()

        devices = []

        results = db.select_all("SELECT * FROM WAKE_ON_LAN WHERE LOCATION == :room", {'room': room})

        for data in results:
            devices.append({'name': data['NAME'], 'id': data['DEVICE'], 'icon': data['ICON']})

        return devices

    def wake_xbox_on_lan(self, user, id, db, check_user=True):
            device = db.select_all("SELECT * FROM XBOX_ONE_WOL WHERE ID == :id",
                        {'id': id})

            if check_user and not user.has_permission(device['LOCATION']):
                return {'result': 'nopermission'}

            ip = device['IP_ADDRESS']
            live_id = device['XBOX_LIVE_ID']

            XBOXOneAPI().xbox_wake_up(ip, live_id)

    def get_xbox_devices(self, user, room, db: Database = None):
        if db is None:
            db = Database()
        if not user.has_permission(room):
            return Status(type=STATUS_NO_PERMISSION).get_dict()

        devices = []
        results = db.select_all("SELECT * FROM XBOX_ONE_WOL WHERE LOCATION == :room", {'room': room})

        for data in results:
            devices.append({'name': data['NAME'], 'id': data['ID'], 'icon': data['ICON']})

        return devices