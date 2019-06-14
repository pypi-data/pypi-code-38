#!/usr/bin/python
# -*- coding: utf-8 -*-
from Homevee.DeviceAPI.get_modes import get_modes
from Homevee.Exception import NoPermissionException
from Homevee.Helper import Logger
from Homevee.Item import Item
from Homevee.Item.Room import Room
from Homevee.Item.User import User
from Homevee.Manager.ControlManager.BlindsManager import BlindsManager
from Homevee.Manager.ControlManager.DimmerManager import DimmerManager
from Homevee.Manager.ControlManager.EnergyDataManager import EnergyDataManager
from Homevee.Manager.ControlManager.RGBLightManager import RGBLightManager
from Homevee.Manager.ControlManager.ThermostatManager import ThermostatManager
from Homevee.Manager.ControlManager.ToggleManager import ToggleManager
from Homevee.Manager.ControlManager.WakeOnLanManager import WakeOnLanManager
from Homevee.Manager.SceneManager import SceneManager
from Homevee.Manager.SensorDataManager import SensorDataManager
from Homevee.Manager.TriggerManager import TriggerManager
from Homevee.Utils.Database import Database
from Homevee.Utils.DeviceTypes import *

CONTROL_TYPE_SWITCH = "switch"
CONTROL_TYPE_VALUE = "value"
CONTROL_TYPE_DIMMER = "dimmer"
CONTROL_TYPE_TOOGLE = "toggle"
CONTROL_TYPE_TRIGGER = "trigger"
CONTROL_TYPE_RGB = "rgb"
CONTROL_TYPE_HEATING = "heating"
CONTROL_TYPE_SCENES = "scenes"
CONTROL_TYPE_WOL = "wwakeonlan"
CONTROL_TYPE_XBOXONE = "xboxone"
CONTROL_TYPE_BLINDS = "blinds"



class RoomDataManager():
    def __init__(self):
        return

    def get_room_data(self, user: User, room, db: Database = None) -> list:
        if db is None:
            db = Database()
        if not user.has_permission(room):
            raise NoPermissionException

        roomdata = []

        room = Item.load_from_db(Room, room, db)

        #Schalter abfragen
        switchdata = get_modes(user, room, "", "")
        for item in switchdata:
            roomdata.append({'name': item['name'], 'id': item['id'], 'devicetype':item['device_type'],
                'icon': item['icon'], 'type': CONTROL_TYPE_SWITCH, 'value': item['mode']})

        #Dimmer
        dimmerdata = DimmerManager().get_dimmers(user, room)
        for item in dimmerdata:
            roomdata.append({'name': item['name'], 'id': item['device'], 'devicetype': item['type'],
                             'icon': item['icon'], 'type': CONTROL_TYPE_DIMMER, 'value': item['value']})

        #Toggle
        toggledata = ToggleManager().get_toggle_devices(user, room)
        for item in toggledata:
            roomdata.append({'name': item['name'], 'id': item['id'], 'devicetype':item['type'],
                'icon': item['icon'], 'type': CONTROL_TYPE_TOOGLE, 'value': ''})

        #Trigger
        triggerdata = TriggerManager().get_triggers(user, room)
        for item in triggerdata:
            roomdata.append({'name': item['name'], 'id': item['id'], 'devicetype':item['type'],
                'icon': item['icon'], 'type': CONTROL_TYPE_TRIGGER, 'value': ''})

        #RGB
        rgbdata = RGBLightManager().get_rgb_devices(user, room)
        for item in rgbdata:
            Logger.log(item)
            roomdata.append({'name': item['name'], 'devicetype':item['type'], 'id': item['id'],
                'icon': item['icon'], 'type': CONTROL_TYPE_RGB, 'value': item['value']})

        #Thermostate
        thermostat_data = ThermostatManager().get_thermostats(user, room)
        for item in thermostat_data[0]['thermostat_array']:
            roomdata.append({'name': item['name'], 'id': item['id'], 'devicetype': item['type'],
                             'icon': item['icon'], 'type': CONTROL_TYPE_HEATING, 'value': item['data']['value'],
                             'step': 0.5, 'min': item['data']['min'], 'max': item['data']['max']})

        #Sensoren abfragen
        sensordata = SensorDataManager().get_sensor_data(user, room)
        for item in sensordata[0]['value_array']:
            roomdata.append({'name': item['name'], 'id': item['id'], 'devicetype': item['device_type'],
                             'icon': item['icon'], 'type': CONTROL_TYPE_VALUE, 'value': item['value']})

        #Szenen abfragen
        scenes = SceneManager().get_scenes(user, room)
        if len(scenes) > 0:
            roomdata.append({'name': "Szenen", 'id': "scenes", 'devicetype': "scenes",
                             'icon': "scenes", 'type': CONTROL_TYPE_SCENES, 'value': ""})

        #WOL abfragen
        wol_devices = WakeOnLanManager().get_wol_devices(user, room)
        for item in wol_devices:
            roomdata.append({'name': item['name'], 'id': item['id'], 'devicetype': WAKE_ON_LAN,
                             'icon': item['icon'], 'type': CONTROL_TYPE_WOL})

        #XBOX ONE WOL abfragen
        xbox_devices = WakeOnLanManager().get_xbox_devices(user, room)
        for item in xbox_devices:
            roomdata.append({'name': item['name'], 'id': item['id'], 'devicetype': XBOX_ONE_WOL,
                             'icon': item['icon'], 'type': CONTROL_TYPE_XBOXONE})

        #Jalousie-Steuerung
        blind_controls = BlindsManager().get_blinds(user, room)
        for item in blind_controls:
            roomdata.append({'name': item['name'], 'id': item['id'], 'devicetype': item['type'],
                             'icon': item['icon'], 'type': CONTROL_TYPE_BLINDS, 'value': item['value']})

        #Strom-Messgeräte
        power_usage_devices = EnergyDataManager().get_power_usage_devices(user, room)
        for item in power_usage_devices:
            roomdata.append({'name': item['name'], 'id': item['id'], 'devicetype': item['devicetype'],
                             'icon': item['icon'], 'type': CONTROL_TYPE_VALUE, 'value': item['value']})

        return roomdata