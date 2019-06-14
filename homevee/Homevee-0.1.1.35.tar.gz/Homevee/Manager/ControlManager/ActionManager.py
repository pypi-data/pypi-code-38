#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

from Homevee.DeviceAPI.set_modes import set_modes
from Homevee.Item.Status import *
from Homevee.Manager.ControlManager.BlindsManager import BlindsManager
from Homevee.Manager.ControlManager.RGBLightManager import RGBLightManager
from Homevee.Manager.ControlManager.ThermostatManager import ThermostatManager
from Homevee.Manager.ControlManager.WakeOnLanManager import WakeOnLanManager
from Homevee.Utils.Database import Database
from Homevee.Utils.DeviceTypes import *
from Homevee.Utils.NotificationManager import NotificationManager


class ActionManager():
    def __init__(self):
        return

    def run_scene(self, user, id, db: Database = None):
        if db is None:
            db = Database()

        result = db.select_one("SELECT * FROM SCENES WHERE ID = :id",
                    {'id': id})

        if (result is None):
            return None

        id = result['ID']

        action_data = result['ACTION_DATA']

        action_data = json.loads(action_data)

        # run actions
        self.run_actions(user, action_data)

        return Status(type=STATUS_OK).get_dict()

    def run_actions(self, user, action_data, db: Database = None):
        if db is None:
            db = Database()
        for action in action_data:
            if action['type'] == "push_notification":
                msg = action['message']
                users = action['users']
                NotificationManager().send_notification_to_users(users, "Homevee", msg)
            elif action['type'] == "run_scene":
                scene_id = action['id']
                self.run_scene(user, scene_id)
            elif action['type'] == 'control_device':
                device_type = action['devicetype']
                device_id = action['id']

                if device_type in [FUNKSTECKDOSE, URL_TOGGLE, URL_SWITCH, ZWAVE_SWITCH]:
                    set_modes(user, device_type, device_id, action['value'], db, False)
                elif device_type == WAKE_ON_LAN:
                    WakeOnLanManager().wake_on_lan(user, device_id, db, False)
                elif device_type == XBOX_ONE_WOL:
                    WakeOnLanManager().wake_xbox_on_lan(user, device_id, db, False)
                elif device_type in [ZWAVE_THERMOSTAT, MAX_THERMOSTAT, RADEMACHER_THERMOSTAT]:
                    ThermostatManager().heating_control(user, device_type, device_id, action['value'], db, False)
                elif device_type in [RADEMACHER_BLIND_CONTROL]:
                    BlindsManager().set_blinds(user, device_type, device_id, action['value'], db, False)
                elif device_type in [PHILIPS_HUE_LIGHT, URL_RGB_LIGHT]:
                    data = json.loads(action['value'])
                    RGBLightManager().rgb_control(user, device_type, device_id, data['mode'], data['brightness'], data['color'], db, False)