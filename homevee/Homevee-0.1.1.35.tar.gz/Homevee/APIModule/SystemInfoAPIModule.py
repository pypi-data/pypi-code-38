from Homevee.APIModule import APIModule
from Homevee.Item.Status import *
from Homevee.Manager.SystemInfoManager import SystemInfoManager

ACTION_KEY_GET_SYSTEM_INFO = "getsysteminfo"

class SystemInfoAPIModule(APIModule):
    def __init__(self):
        super(SystemInfoAPIModule, self).__init__()
        self.system_info_manager = SystemInfoManager()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_GET_SYSTEM_INFO: self.get_system_info
        }
        return mappings

    def get_system_info(self, user, request, db) -> Status:
        try:
            system_info = self.system_info_manager.get_system_info()
            return Status(type=STATUS_OK, data={'systeminfo': system_info})
        except:
            return Status(type=STATUS_ERROR)
