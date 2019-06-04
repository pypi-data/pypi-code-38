#!/usr/bin/python
# -*- coding: utf-8 -*-
import traceback
import urllib.error
import urllib.parse
import urllib.request

from Homevee.DeviceAPI import zwave
from Homevee.Helper import Logger
from Homevee.Item.Device import Device
from Homevee.Item.Device.Switch.Funksteckdose import Funksteckdose
from Homevee.Item.Status import *
from Homevee.Utils.DeviceTypes import *


def set_modes(user, type, id, mode, db, check_user=True):
    if type == FUNKSTECKDOSE:
        return set_socket(user, id, mode, db, check_user)
    elif type == ZWAVE_SWITCH:
        return set_zwave_switch(user, id, mode, db, check_user)
    elif type == URL_SWITCH:
        return set_url_switch_binary(user, id, mode, db, check_user)
    elif type == URL_TOGGLE:
        return set_url_toggle(user, id, db, check_user)
    else:
        return Status(type=STATUS_NO_SUCH_TYPE).get_dict()

def set_url_switch_binary(user, id, mode, db, check_user=True):
    data = db.select_one("SELECT * FROM URL_SWITCH_BINARY WHERE ID == :id",
                {'id': id})

    if check_user and not user.has_permission(data['LOCATION']):
        return {'result': 'nopermission'}

    if mode == "":
        urllib.request.urlopen(data['URL_ON'])
    else:
        urllib.request.urlopen(data['URL_OFF'])

    return Status(type=STATUS_OK).get_dict()

def set_url_toggle(user, id, db, check_user=True):
    data = db.select_one("SELECT * FROM URL_TOGGLE WHERE ID == :id",
                {'id': id})

    if check_user and not user.has_permission(data['LOCATION']):
        return {'result': 'nopermission'}

    urllib.request.urlopen(data['TOGGLE_URL'])

    return Status(type=STATUS_OK).get_dict()

def set_socket(user, id, mode, db, check_user=True):
    try:
        funksteckdose = Device.load_from_db(Funksteckdose, id)

        if check_user and not user.has_permission(funksteckdose.location):
            return {'result': 'nopermission'}

        if(funksteckdose.set_mode(mode)):
            return Status(type=STATUS_OK).get_dict()
    except:
        if(Logger.IS_DEBUG):
                traceback.print_exc()
    return Status(type=STATUS_ERROR).get_dict()

def set_zwave_switch(user, id, mode, db, check_user=True):
    try:

        cur = db.cursor()
        data = db.select_one("SELECT * FROM ZWAVE_SWITCHES WHERE ID == :device",
                    {'device': id})

        if check_user and not user.has_permission(data['LOCATION']):
            return {'result': 'nopermission'}

        device_id = data['ID']

        state = "on" if (int(mode) == 1) else "off"

        result = zwave.device_control.set_binary_device(device_id, state)

        if result['code'] == 200:
            db.update("UPDATE ZWAVE_SWITCHES SET VALUE = :value WHERE ID = :id",
                        {'value': mode, 'id': id})

            return Status(type=STATUS_OK).get_dict()
    except Exception as e:
        if Logger.IS_DEBUG:
            if(Logger.IS_DEBUG):
                traceback.print_exc()
        return Status(type=STATUS_ERROR).get_dict()

def set_diy_switch(id, mode, db, check_user=True):
    return