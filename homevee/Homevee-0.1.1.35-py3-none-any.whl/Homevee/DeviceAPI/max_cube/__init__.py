#!/usr/bin/python
# -*- coding: utf-8 -*-

from pymax.cube import Cube

from Homevee.Helper import Logger
from Homevee.Item import Item
from Homevee.Item.Gateway import Gateway, MAX_CUBE
from Homevee.Utils.Database import Database


class MaxCubeAPI:
    def __init__(self):
        return

def get_devices(ip):
    thermostats = []
    try:
        with Cube(ip) as cube:
            for room in cube.rooms:
                for device in room.devices:
                    Logger.log(device)
                    thermostat = {'title': device.name, 'id': device.serial, 'room': room.name}

                    thermostats.append(thermostat)
    except:
        thermostats = []

    return thermostats


def set_temp(id, value, db: Database = None):
    if db is None:
        db = Database()
    gateway = Item.load_from_db(Gateway, MAX_CUBE)

    with Cube(gateway.ip) as cube:
        for room in cube.rooms:
            for device in room.devices:
                if id == device.serial:
                    result = cube.set_mode_manual(room.room_id, room.rf_address, float(value))

                    Logger.log(result)

                    db.update("UPDATE MAX_THERMOSTATS SET LAST_TEMP = :temp WHERE ID == :id",
                                {'temp': value, 'id': id})