#!/usr/bin/python
# -*- coding: utf-8 -*-
from Homevee.Exception import NoSuchTypeException
from Homevee.Item.Device import Device
from Homevee.Item.Device.Switch.Funksteckdose import Funksteckdose
from Homevee.Item.Status import *
from Homevee.Utils.Database import Database
from Homevee.Utils.DeviceTypes import *


def get_mode(type, id, db: Database = None):
    if db is None:
        db = Database()
    module_map = {
        FUNKSTECKDOSE: Funksteckdose
    }

    if type not in module_map:
        raise NoSuchTypeException("type "+type+" does not exist")

    item = Device.load_from_db(module_map[type], id)

    return item.mode

def get_modes(user, room, type, id, db: Database = None):
    if db is None:
        db = Database()
    if not user.has_permission(room):
        return Status(type=STATUS_NO_PERMISSION).get_dict()

    if id is None or id == "":
        modi = []

        devices = {}

        modules = [Funksteckdose]

        for module in modules:
            devices = Device.get_all(module, room, db)

            for device in devices:
                item = device.get_dict()
                modi.append(item)

        return modi

    else:
        return get_mode(type, id, db)