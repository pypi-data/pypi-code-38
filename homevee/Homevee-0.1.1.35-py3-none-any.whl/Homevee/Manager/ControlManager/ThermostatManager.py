#!/usr/bin/python
# -*- coding: utf-8 -*-
from Homevee.Item.Device import Device
from Homevee.Item.Device.Thermostat.MaxThermostat import *
from Homevee.Item.Device.Thermostat.RademacherThermostat import *
from Homevee.Item.Device.Thermostat.ZWaveThermostat import *
from Homevee.Item.Room import Room
from Homevee.Item.Status import *
from Homevee.Utils.DeviceTypes import *

class ThermostatManager:
    def __init__(self):
        return

    def heating_control(self, user, type, id, value, db, check_user=True):
        if type == MAX_CUBE:
            module = MaxThermostat
        elif type == ZWAVE_THERMOSTAT:
            module = ZWaveThermostat
        elif type == RADEMACHER_THERMOSTAT:
            module = RademacherThermostat
        else:
            return Status(type=STATUS_NO_SUCH_TYPE).get_dict()

        thermostat = Device.load_from_db(module, id)

        if check_user and not user.has_permission(thermostat.location):
            return Status(type=STATUS_NO_PERMISSION).get_dict()

        if(thermostat.set_temp(value)):
            return Status(type=STATUS_OK).get_dict()
        else:
            return Status(type=STATUS_ERROR).get_dict()

    def control_room_heating(self, user, room, value, db: Database = None):
        if db is None:
            db = Database()
            devices = self.get_thermostats(user, room, db)[0]['thermostat_array']
            for device in devices:
                id = device['id']
                type = device['type']
                result = self.heating_control(user, type, id, value, db)
                if 'result' not in result or result['result'] != "ok":
                    return Status(type=STATUS_ERROR).get_dict()
            return Status(type=STATUS_OK).get_dict()

    def get_thermostat_info(self, user, room, type, id, db: Database = None):
        if db is None:
            db = Database()
        if not user.has_permission(room):
            return Status(type=STATUS_NO_PERMISSION).get_dict()

        module_map = {
            ZWAVE_THERMOSTAT: ZWaveThermostat,
            MAX_THERMOSTAT: MaxThermostat,
            RADEMACHER_THERMOSTAT: RademacherThermostat
        }

        if type not in module_map:
            return Status(type=STATUS_NO_SUCH_TYPE).get_dict()

        thermostat = Device.load_from_db(module_map[type], id)

        min, max = thermostat.get_min_max()
        return {'value': thermostat.temp, 'min': min, 'max': max}

    def get_thermostats(self, user, room, db: Database = None):
        if db is None:
            db = Database()
        if isinstance(room, Room):
            rooms = [room]
        elif room == "all":
            rooms = Room.load_all(db)
        else:
            rooms = Room.load_all_ids_from_db([room])

        thermostats = []

        for room in rooms:
            if not user.has_permission(room.id):
                continue

            thermostat_array = []

            modules = [ZWaveThermostat, MaxThermostat, RademacherThermostat]

            for module in modules:
                thermostat_items = Device.get_all(module, room)
                for thermostat in thermostat_items:
                    min, max = thermostat.get_min_max()
                    thermostat_data = {'name': thermostat.name, 'id': thermostat.id, 'type': thermostat.get_device_type(),
                                       'icon': thermostat.icon, 'data': {'value': thermostat.temp, 'min': min, 'max': max}}
                    thermostat_array.append(thermostat_data)

            room_thermostats = {'name': room.name, 'location': room.id, 'icon': room.icon,
                                'thermostat_array': thermostat_array}
            thermostats.append(room_thermostats)

        return thermostats
