#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

import requests

from Homevee.Exception import NoPermissionException
from Homevee.Helper import Logger
from Homevee.Item.Gateway import *
from Homevee.Item.Status import *


def set_light_mode(user, id, mode, saturation, brightness, color, db, check_user=True):
    result = db.select_one("SELECT LOCATION FROM PHILIPS_HUE_LIGHTS WHERE ID = :id", {'id': id})

    if check_user and not user.has_permission(result['LOCATION']):
        raise NoPermissionException

    gateway = Item.load_from_db(Gateway, PHILIPS_HUE_BRIDGE)

    if mode == True or mode == "1":
        mode = True
    else:
        mode = False

    data = {}

    result = db.select_one("SELECT * FROM PHILIPS_HUE_LIGHTS WHERE ID = :id", {'id': id})

    if color is not None:
        rgb = tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
        x, y, z = rgb_to_xy(rgb)
        data['xy'] = [x, y]
        data['sat'] = int(z * 255)
    else:
        data['hue'] = result['HUE']

    if mode is not None:
        data['on'] = mode
    else:
        data['on'] = result['IS_ON'] == 1

    if brightness is not None:
        data['bri'] = int(float(brightness) * 255 / 100)
    else:
        data['bri'] = int(result['BRIGHTNESS'])

    Logger.log("rgb")

    response = requests.put("http://" + gateway.ip + "/api/" + gateway.key1 + "/lights/" + str(id) + "/state",
                            data=json.dumps(data))

    Logger.log(response.text)

    update_light_info(id, mode, color, saturation, brightness)

    return Status(type=STATUS_OK).get_dict()


def rgb_to_xy(rgb):
    red, green, blue = rgb

    if (red > 0.04045):
        red = pow((red + 0.055) / (1.0 + 0.055), 2.4)
    else:
        red = (red / 12.92)

    if (green > 0.04045):
        green = pow((green + 0.055) / (1.0 + 0.055), 2.4)
    else:
        green = (green / 12.92)

    if (blue > 0.04045):
        blue = pow((blue + 0.055) / (1.0 + 0.055), 2.4)
    else:
        blue = (blue / 12.92)

    X = red * 0.664511 + green * 0.154324 + blue * 0.162028
    Y = red * 0.283881 + green * 0.668433 + blue * 0.047685
    Z = red * 0.000088 + green * 0.072310 + blue * 0.986039

    if (X + Y + Z) == 0:
        fx = 0
        fy = 0
        fz = 0
    else:
        fx = X / (X + Y + Z)
        fy = Y / (X + Y + Z)
        fz = Z / (X + Y + Z)

    if (fx != fx):
        fx = 0.0

    if (fy != fy):
        fy = 0.0

    if (fz != fz):
        fz = 0.0

    return (fx, fy, fz)


def get_devices(db):
    gateway = Item.load_from_db(Gateway, PHILIPS_HUE_BRIDGE)

    try:
        response = requests.get("http://" + gateway.ip + "/api/" + gateway.key1 + "/lights").text

        Logger.log(response)

        data = json.loads(response)

        ids = list(data.keys())

        devices = []

        for id in ids:
            item = data[id]
            device_item = {'title': item['name'], 'id': id, 'room': None, 'type': 'light'}
            devices.append(device_item)
    except:
        Logger.log("Could not connect to Hue-Bridge...")

    return devices


def get_light_info(id, db: Database = None):
    if db is None:
        db = Database()


    gateway = Item.load_from_db(Gateway, PHILIPS_HUE_BRIDGE, db)

    try:
        request = requests.get("http://" + gateway.ip + "/api/" + gateway.key1 + "/lights/" + str(id))

        code = request.status_code

        if (code != 200):
            return False

        data = json.loads(request.text)

        mode = data['state']['on']
        brightness = int(float(data['state']['bri']) / 255 * 100)
        saturation = int(float(data['state']['sat']) / 255 * 100)
        hue = data['state']['hue']

        update_light_info(id, mode, hue, saturation, brightness, db)

        return True
    except:
        Logger.log("Could not connect to Hue-Bridge...")
        return False


def update_light_info(id, mode, hue, saturation, brightness, db: Database = None):
    if db is None:
        db = Database()
    if saturation is None:
        saturation = 255
    if brightness is None:
        brightness = 255
    db.update("""UPDATE PHILIPS_HUE_LIGHTS SET IS_ON = :mode, BRIGHTNESS = :bri, 
        SATURATION = :sat, HUE = :hue WHERE ID = :id""",
              {'mode': mode, 'bri': brightness, 'sat': saturation, 'hue': hue, 'id': id})
