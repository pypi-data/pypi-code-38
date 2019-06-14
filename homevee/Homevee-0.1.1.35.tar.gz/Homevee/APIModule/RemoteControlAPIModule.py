from Homevee.APIModule import APIModule
from Homevee.Item.Status import *
from Homevee.Manager.RemoteControlManager import RemoteControlManager

ACTION_KEY_SET_REMOTE_DATA = "setremotedata"
ACTION_KEY_GET_REMOTE_DATA = "getremotedata"
ACTION_KEY_SET_REMOTE_CONTROL_ENABLED = "setremotecontrolenabled"
ACTION_KEY_CONNECT_REMOTE_ID_WITH_ACCOUNT = "connectremoteidwithaccount"

class RemoteControlAPIModule(APIModule):
    def __init__(self):
        super(RemoteControlAPIModule, self).__init__()
        self.remote_control_manager = RemoteControlManager()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_SET_REMOTE_DATA: self.set_remote_data,
            ACTION_KEY_GET_REMOTE_DATA: self.get_remote_data,
            ACTION_KEY_SET_REMOTE_CONTROL_ENABLED: self.set_remote_control_enabled,
            ACTION_KEY_CONNECT_REMOTE_ID_WITH_ACCOUNT: self.connect_remote_id_with_account
        }

        return mappings

    def set_remote_data(self, user, request, db):
        try:
            self.remote_control_manager.save_remote_data(user, request['remote_id'], request['linked_account'], db)
            return Status(type=STATUS_OK)
        except:
            return Status(type=STATUS_ERROR)

    def get_remote_data(self, user, request, db):
        try:
            data = self.remote_control_manager.load_remote_data(user, db)
            return Status(type=STATUS_OK, data=data)
        except:
            return Status(type=STATUS_ERROR)

    def set_remote_control_enabled(self, user, request, db):
        try:
            self.remote_control_manager.set_remote_control_enabled(user, request['enabled'], db)
            return Status(type=STATUS_OK)
        except:
            return Status(type=STATUS_ERROR)

    def connect_remote_id_with_account(self, user, request, db):
        try:
            success = self.remote_control_manager.connect_remote_id_with_account(user,
                                    request['accountname'], request['accountsecret'], db)
            if success:
                return Status(type=STATUS_OK)
            else:
                return Status(type=STATUS_ERROR)
        except:
            return Status(type=STATUS_ERROR)