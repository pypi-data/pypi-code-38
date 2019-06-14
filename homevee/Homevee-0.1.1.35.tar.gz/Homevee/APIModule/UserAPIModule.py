from Homevee.APIModule import APIModule
from Homevee.Item.Status import *
from Homevee.Manager.UserManager import UserManager

ACTION_KEY_GET_USERS = "getusers"
ACTION_KEY_ADD_EDIT_USER = "addedituser"
ACTION_KEY_DELETE_USER = "deleteuser"
ACTION_KEY_UPDATE_FCM_TOKEN = "updatefcmtoken"

class UserAPIModule(APIModule):
    def __init__(self):
        super(UserAPIModule, self).__init__()
        self.user_manager = UserManager()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_GET_USERS: self.get_users,
            ACTION_KEY_ADD_EDIT_USER: self.add_edit_user,
            ACTION_KEY_DELETE_USER: self.delete_user,
            ACTION_KEY_UPDATE_FCM_TOKEN: self.update_fcm_token
        }

        return mappings

    def get_users(self, user, request, db):
        users = self.user_manager.get_users(user, db)
        return Status(type=STATUS_OK, data={'users':self.user_manager.get_dict_list_from_item_list(users)})

    def add_edit_user(self, user, request, db):
        self.user_manager.add_edit_user(user, request['name'], request['psw'], request['ip'],
                                    request['permissions'], db)
        return Status(type=STATUS_OK)

    def delete_user(self, user, request, db):
        self.user_manager.delete_user(user, request['name'], db)
        return Status(type=STATUS_OK)

    def update_fcm_token(self, user, request, db):
        self.user_manager.set_user_fcm_token(user, request['token'], db)
        return Status(type=STATUS_OK)