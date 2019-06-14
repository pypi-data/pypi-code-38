from Homevee.APIModule import APIModule
from Homevee.Item.Status import *
from Homevee.Manager.ControlManager.EnergyDataManager import EnergyDataManager

ACTION_KEY_GET_ENERGY_DATA = "getenergydata"
ACTION_KEY_GET_DEVICE_ENERGY_DATA = "getdeviceenergydata"
ACTION_KEY_GET_ENERGY_COURSE = "getenergycourse"
ACTION_KEY_SET_POWER_COST = "setpowercost"
ACTION_KEY_GET_POWER_COST = "getpowercost"

class EnergyDataAPIModule(APIModule):
    def __init__(self):
        super(EnergyDataAPIModule, self).__init__()
        self.energy_manager = EnergyDataManager()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_GET_ENERGY_DATA: self.get_energy_data,
            ACTION_KEY_GET_DEVICE_ENERGY_DATA: self.get_device_energy_data,
            ACTION_KEY_GET_ENERGY_COURSE: self.get_energy_course,
            ACTION_KEY_GET_POWER_COST: self.get_power_cost,
            ACTION_KEY_SET_POWER_COST: self.set_power_cost
        }

        return mappings

    def get_energy_data(self, user, request, db):
        data = self.energy_manager.get_energy_data(user, request['room'], request['devicetype'],
                                                           request['deviceid'],
                                                           request['von'], request['bis'], db)
        return Status(type=STATUS_OK, data={'energydata': data})

    def get_device_energy_data(self, user, request, db):
        data = self.energy_manager.get_device_energy_data(user, request['room'], request['devicetype'],
                                                                  request['deviceid'],
                                                                  request['von'], request['bis'], db)
        return Status(type=STATUS_OK, data=data)

    def get_energy_course(self, user, request, db):
        data = self.energy_manager.get_energy_course(user, request['room'], request['von'], request['bis'], db)
        return Status(type=STATUS_OK, data=data)

    def get_power_cost(self, user, request, db):
        data = self.energy_manager.set_power_cost(user, request['cost'], db)
        return Status(type=STATUS_OK, data={'powercost': data})

    def set_power_cost(self, user, request, db):
        self.energy_manager.get_power_cost(user, db)
        return Status(type=STATUS_OK)