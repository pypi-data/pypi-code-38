from Homevee.APIModule import APIModule
from Homevee.Item.Status import *
from Homevee.Manager.RoomDataManager import RoomDataManager

ACTION_KEY_GET_ROOMDATA = "getroomdata"

class RoomDataAPIModule(APIModule):
    def __init__(self):
        super(RoomDataAPIModule, self).__init__()
        self.room_data_manager = RoomDataManager()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_GET_ROOMDATA: self.get_room_data,
        }
        return mappings

    def get_room_data(self, user, request, db) -> Status:
        rooms = self.room_data_manager.get_room_data(user, request['room'], db)
        return Status(type=STATUS_OK, data={'roomdata':rooms})