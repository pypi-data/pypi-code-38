#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

from Homevee.Exception import NoPermissionException
from Homevee.Item.Device import Device
from Homevee.Item.HeatingSchemeItem import HeatingSchemeItem
from Homevee.Utils.Database import Database


class HeatingSchemeManager:
    def __init__(self):
        return

    def add_edit_heating_scheme_item(self, user, id, time, value, active, days, data, db: Database = None):
        if db is None:
            db = Database()
        if not user.has_permission("admin"):
            raise NoPermissionException

        params = {'time': time, 'value': value, 'active': active}

        if id == "" or id is None:
            db.insert("INSERT INTO HEATING_SCHEME (TIME, VALUE, ACTIVE) VALUES (:time, :value, :active)",
                        params)
        else:
            params['id'] = id
            db.update("UPDATE HEATING_SCHEME SET TIME = :time, VALUE = :value, ACTIVE = :active WHERE ID = :id",
                params)

        #HEATING_SCHEME_DAYS bearbeiten
        db.delete("DELETE FROM 'HEATING_SCHEME_DAYS' WHERE HEATING_SCHEME_ID = :id", {'id': id})

        day_array = json.loads(days)

        for day in day_array:
            db.insert("INSERT INTO 'HEATING_SCHEME_DAYS' (HEATING_SCHEME_ID, WEEKDAY_ID) VALUES (:id, :weekday_id)",
                {'id': id, 'weekday_id': day})

        #HEATING_SCHEME_DEVICES bearbeiten
        db.delete("DELETE FROM 'HEATING_SCHEME_DEVICES' WHERE ID = :id", {'id': id})

        device_array = json.loads(data)

        for device in device_array['devices']:
            db.insert("INSERT INTO 'HEATING_SCHEME_DEVICES' (ID, LOCATION, TYPE, DEVICE_ID) VALUES (:id, :location, :type, :device_id)",
                {'id': id, 'location': device['location'], 'type': device['type'], 'device_id': device['id']})

    def delete_heating_scheme_item(self, user, id, db: Database = None):
        if db is None:
            db = Database()
        if not user.has_permission("admin"):
            raise NoPermissionException

        heating_scheme_item = Device.load_from_db(HeatingSchemeItem, id, db)
        heating_scheme_item.delete(db)

    def get_heating_scheme_items(self, user, day, rooms, db: Database = None):
        if db is None:
            db = Database()
        if not user.has_permission("admin"):
            raise NoPermissionException

        params = {'day': day}
        query_in_rooms_string = ""

        if rooms is not None and rooms != "":
            params['rooms'] = rooms
            query_in_rooms_string = "AND LOCATION IN (:rooms)"

        results = db.select_all("SELECT HEATING_SCHEME.ID, TIME, VALUE, ACTIVE, WEEKDAY_ID, ROOMS.NAME as LOCATION, TYPE, DEVICE_ID FROM HEATING_SCHEME, HEATING_SCHEME_DAYS, HEATING_SCHEME_DEVICES, ROOMS WHERE HEATING_SCHEME.ID = HEATING_SCHEME_DAYS.HEATING_SCHEME_ID AND HEATING_SCHEME.ID = HEATING_SCHEME_DEVICES.ID AND HEATING_SCHEME_DEVICES.LOCATION = ROOMS.LOCATION AND WEEKDAY_ID = :day "+query_in_rooms_string+" ORDER BY TIME",
                    params)

        heating_scheme_items = {}
        heating_scheme_data = {}

        for result in results:
            if result['ID'] not in heating_scheme_data:
                heating_scheme_data[result['ID']] = []

            heating_scheme_data[result['ID']].append({'location': result['LOCATION'], 'type': result['TYPE'], 'device':result['DEVICE_ID']})

            heating_scheme_items[result['ID']] = {'time': result['TIME'], 'value': result['VALUE'], 'isactive': (True if result['ACTIVE']=="true" else False)}

        for result in results:
            heating_scheme_items[result['ID']]['data'] = heating_scheme_data[result['ID']]

        return heating_scheme_items

    def get_heating_scheme_item_data(self, user, id, db: Database = None):
        if db is None:
            db = Database()
        heating_scheme_item = {}

        params = {'id': id}

        #Tage abfragen
        chosen_days = []
        results = db.select_all("SELECT WEEKDAY_ID FROM HEATING_SCHEME_DAYS WHERE HEATING_SCHEME_ID == :id", params)
        for day in results:
            chosen_days.append(int(day['WEEKDAY_ID']))
        heating_scheme_item['days'] = chosen_days

        #Geräte abfragen
        devices = []
        results = db.select_all("SELECT * FROM HEATING_SCHEME_DEVICES WHERE ID == :id", params)
        for device in results:
            devices.append({'id': device['DEVICE_ID'], 'type': device['TYPE'], 'location': device['LOCATION']})
        heating_scheme_item['devicearray'] = json.dumps({'devices': devices})

        #Daten
        scheme_item_data = db.select_one("SELECT * FROM HEATING_SCHEME WHERE ID == :id", params)

        heating_scheme_item['value'] = float(scheme_item_data['VALUE'])
        heating_scheme_item['time'] = scheme_item_data['TIME']
        heating_scheme_item['active'] = scheme_item_data['ACTIVE']

        return heating_scheme_item

    def set_heating_scheme_item_active(self, user, id, active, db: Database = None):
        if db is None:
            db = Database()
        if not user.has_permission("admin"):
            raise NoPermissionException

        db.update("UPDATE HEATING_SCHEME SET ACTIVE = :active WHERE ID = :id", {'active': active, 'id': id})

    def is_heating_scheme_active(self, user, db: Database = None):
        if db is None:
            db = Database()
        if not user.has_permission("admin"):
            raise NoPermissionException

        is_active = db.get_server_data("HEATING_SCHEME_ACTIVE")

        return is_active=="true"

    def set_heating_scheme_active(self, user, active, db: Database = None):
        if db is None:
            db = Database()
        if not user.has_permission("admin"):
            raise NoPermissionException

        db.set_server_data("HEATING_SCHEME_ACTIVE", active)