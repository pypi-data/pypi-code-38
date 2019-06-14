#!/usr/bin/python
# -*- coding: utf-8 -*-

from Homevee.Utils.Database import Database

class ToggleManager:
    def __init__(self):
        return

    def get_toggle_devices(self, user, room, db: Database = None):
        if db is None:
            db = Database()
        devices = []
        results = db.select_all("SELECT * FROM URL_TOGGLE WHERE LOCATION = :location",
                    {'location': room})

        for toggle in results:
            devices.append({'name': toggle['NAME'], 'id': toggle['ID'], 'type': 'URL-Toggle',
                'icon': toggle['ICON']})

        return devices