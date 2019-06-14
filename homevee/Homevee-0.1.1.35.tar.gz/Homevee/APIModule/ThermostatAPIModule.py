from Homevee.APIModule import APIModule
from Homevee.Item.Status import *
from Homevee.Manager.ControlManager.ThermostatManager import ThermostatManager

ACTION_KEY_HEATING_CONTROL = "heatingcontrol"
ACTION_KEY_CONTROL_ROOM_HEATING = "controlroomheating"
ACTION_KEY_GET_THERMOSTATS = "getthermostats"

class ThermostatAPIModule(APIModule):
    def __init__(self):
        super(ThermostatAPIModule, self).__init__()
        self.thermostat_manager = ThermostatManager()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_HEATING_CONTROL: self.heating_control,
            ACTION_KEY_CONTROL_ROOM_HEATING: self.control_room_heating,
            ACTION_KEY_GET_THERMOSTATS: self.get_thermostats
        }

        return mappings

    def heating_control(self, user, request, db):
        self.thermostat_manager.heating_control(user, request['type'], request['id'], request['value'], db)
        return Status(type=STATUS_OK)

    def control_room_heating(self, user, request, db):
        self.thermostat_manager.control_room_heating(user, request['location'], request['value'], db)
        return Status(type=STATUS_OK)

    def get_thermostats(self, user, request, db):
        data = self.thermostat_manager.get_thermostats(user, request['room'], db)
        return Status(type=STATUS_OK, data={'thermostats': data})