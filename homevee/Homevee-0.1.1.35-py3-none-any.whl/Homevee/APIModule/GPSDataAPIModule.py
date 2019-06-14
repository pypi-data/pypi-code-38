from Homevee.APIModule import APIModule
from Homevee.Item.Status import *
from Homevee.Manager.GPSDataManager import GPSDataManager

ACTION_KEY_UPDATE_GPS = "updategps"
ACTION_KEY_GET_GPS_LOCATIONS = "getgpslocations"

class GPSDataAPIModule(APIModule):
    def __init__(self):
        super(GPSDataAPIModule, self).__init__()
        self.gps_data_manager = GPSDataManager()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_UPDATE_GPS: self.update_gps,
            ACTION_KEY_GET_GPS_LOCATIONS: self.get_gps_locations
        }

        return mappings

    def update_gps(self, user, request, db):
        self.gps_data_manager.update_gps(user, request['time'], request['lat'], request['lng'], db)
        return Status(type=STATUS_OK)

    def get_gps_locations(self, user, request, db):
        locations = self.gps_data_manager.get_gps_locations(user, db)
        return Status(type=STATUS_OK, data={'locations':locations})