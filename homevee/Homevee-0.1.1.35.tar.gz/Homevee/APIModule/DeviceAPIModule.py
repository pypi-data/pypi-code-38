from Homevee.APIModule import APIModule
from Homevee.Item.Status import *
from Homevee.Manager.DeviceManager import DeviceManager

ACTION_KEY_ADD_EDIT_DEVICE = "addeditdevice"
ACTION_KEY_DELETE_DEVICE = "deletedevice"
ACTION_KEY_GET_DEVICE_DATA = "getdevicedata"

class DeviceAPIModule(APIModule):
    def __init__(self):
        super(DeviceAPIModule, self).__init__()
        self.device_manager = DeviceManager()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_ADD_EDIT_DEVICE: self.add_edit_device,
            ACTION_KEY_DELETE_DEVICE: self.delete_device,
            ACTION_KEY_GET_DEVICE_DATA: self.get_device_data
        }

        return mappings

    def add_edit_device(self, user, request, db):
        data = self.device_manager.add_edit_device(user, request['id'], request['type'], request['data'], db)
        return Status(type=STATUS_OK, data=data)

    def delete_device(self, user, request, db):
        data = self.device_manager.delete_device(user, request['type'], request['id'], db)
        return Status(type=STATUS_OK, data=data)

    def get_device_data(self, user, request, db):
        data = self.device_manager.get_device_data(user, request['type'], request['id'], db)
        return Status(type=STATUS_OK, data=data)