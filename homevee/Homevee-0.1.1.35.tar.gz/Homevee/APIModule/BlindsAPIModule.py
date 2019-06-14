from Homevee.APIModule import APIModule
from Homevee.Item.Status import *
from Homevee.Manager.ControlManager.BlindsManager import BlindsManager

ACTION_KEY_SET_BLINDS = "setblinds"
ACTION_KEY_SET_ROOM_BLINDS = "setroomblinds"
ACTION_KEY_GET_ALL_BLINDS = "getallblinds"

class BlindsAPIModule(APIModule):
    def __init__(self):
        super(BlindsAPIModule, self).__init__()
        self.blinds_manager = BlindsManager()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_SET_BLINDS: self.set_blinds,
            ACTION_KEY_SET_ROOM_BLINDS: self.set_room_blinds,
            ACTION_KEY_GET_ALL_BLINDS: self.get_all_blinds
        }

        return mappings

    def set_blinds(self, user, request, db):
        self.blinds_manager.set_blinds(user, request['type'], request['id'], request['value'], db)
        return Status(type=STATUS_OK)

    def set_room_blinds(self, user, request, db):
        self.blinds_manager.set_room_blinds(user, request['location'], request['value'], db)
        return Status(type=STATUS_OK)

    def get_all_blinds(self, user, request, db):
        data = self.blinds_manager.get_all_blinds(user, db)
        return Status(type=STATUS_OK, data={'blinds': data})