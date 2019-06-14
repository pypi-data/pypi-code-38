from Homevee.APIModule import APIModule
from Homevee.Item.Status import *
from Homevee.Manager.APIKeyManager import APIKeyManager

ACTION_KEY_GET_API_KEY_DATA = "getapikeydata"
ACTION_KEY_SET_API_KEY = "setapikey"

class APIKeyAPIModule(APIModule):
    def __init__(self):
        super(APIKeyAPIModule, self).__init__()
        self.api_key_manager = APIKeyManager()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_GET_API_KEY_DATA: self.get_api_key_data,
            ACTION_KEY_SET_API_KEY: self.set_api_key
        }

        return mappings

    def get_api_key_data(self, user, request, db):
        data = self.api_key_manager.get_all_api_key_data(user, db)
        return Status(type=STATUS_OK, data={'apikeys': data})

    def set_api_key(self, user, request, db):
        data = self.api_key_manager.set_api_key(user, request['service'], request['apikey'], db)
        return Status(type=STATUS_OK)