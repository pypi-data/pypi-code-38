#!/usr/bin/python
import json

from pymax.cube import Cube

from Homevee.Helper import Logger
from Homevee.Item.Status import *
from Homevee.Utils.Database import Database


def get_devices(cubeip):
    data = []

    with Cube(cubeip) as cube:
        for room in cube.rooms:
            for device in room.devices:
                devicedata = {}

                devicedata['room'] = room.name
                devicedata['title'] = device.name
                # devicedata['temp'] = device.temperature
                devicedata['id'] = device.serial

                data.append(devicedata)

    return json.dumps(data)


def get_device_data(cubeip, deviceid):
    data = {}

    with Cube(cubeip) as cube:
        for room in cube.rooms:
            for device in room.devices:
                if deviceid == device.serial:
                    data['room'] = room.room_id
                    data['addr'] = room.rf_address

                    return data


def get_rooms(cubeip):
    data = []

    with Cube(cubeip) as cube:
        for room in cube.rooms:
            roomdata = {}
            roomdata['name'] = room.name
            Logger.log(room.rf_address)
            # roomdata['address'] = room.rf_address
            roomdata['id'] = room.room_id
            data.append(roomdata)

    return json.dumps(data)


#Sets the temperature
def set_temperature(cubeip, deviceid, temp):
    data = get_device_data(cubeip, deviceid)

    # temperatur berechnen
    tempVal = temp

    with Cube(cubeip) as cube:
        result = cube.set_mode_manual(data['room'], data['addr'], tempVal)

        update_temp(deviceid, temp)
        return Status(type=STATUS_OK).get_dict()


def update_temp(deviceid, temp, db: Database = None):
    if db is None:
        db = Database()
    #TODO sql abfrage anpassen
    db.update("UPDATE MAX_THERMOSTATS SET LAST_TEMP = " + temp + " WHERE ID == '" + deviceid + "';", {})