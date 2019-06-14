from Homevee.APIModule import APIModule
from Homevee.Item.Status import *
from Homevee.Manager.ControlManager.WakeOnLanManager import WakeOnLanManager

ACTION_KEY_WAKE_ON_LAN = "wakeonlan"
ACTION_KEY_START_XBOX_ONE = "startxboxone"

class WakeOnLanAPIModule(APIModule):
    def __init__(self):
        super(WakeOnLanAPIModule, self).__init__()
        self.wol_manager = WakeOnLanManager()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_WAKE_ON_LAN: self.wake_on_lan,
            ACTION_KEY_START_XBOX_ONE: self.start_xbox_one
        }

        return mappings

    def wake_on_lan(self, user, request, db):
        self.wol_manager.wake_on_lan(user, request['id'], db)
        return Status(type=STATUS_OK)

    def start_xbox_one(self, user, request, db):
        self.wol_manager.wake_xbox_on_lan(user, request['id'], db)
        return Status(type=STATUS_OK)