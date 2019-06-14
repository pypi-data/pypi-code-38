from Homevee.APIModule import APIModule
from Homevee.Item.Room import Room
from Homevee.Item.Status import *
from Homevee.Manager.RoomManager import RoomManager

ACTION_KEY_LOGIN = "login"

class LoginAPIModule(APIModule):
    def __init__(self):
        super(LoginAPIModule, self).__init__()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_LOGIN: self.do_login
        }

        return mappings

    def do_login(self, user, request, db):
        rooms = RoomManager().get_rooms(user, db)
        remote_id = db.get_server_data("REMOTE_ID")
        access_token = "ACCESS_TOKEN"
        data = {'remote_id': remote_id, 'access_token': access_token, 'rooms': Room.list_to_dict(rooms)}
        return Status(type=STATUS_OK, data=data)