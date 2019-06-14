from Homevee.APIModule import APIModule
from Homevee.Item.Status import *
from Homevee.Manager.SensorDataManager import SensorDataManager

ACTION_KEY_GET_SENSOR_DATA = "getsensordata"

class SensorDataAPIModule(APIModule):
    def __init__(self):
        super(SensorDataAPIModule, self).__init__()
        self.sensor_data_manager = SensorDataManager()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_GET_SENSOR_DATA: self.get_sensor_data
        }

        return mappings

    def get_sensor_data(self, user, request, db):
        data = self.sensor_data_manager.get_sensor_data(user, request['room'], db)
        return Status(type=STATUS_OK, data={'values': data})