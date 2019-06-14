from Homevee.APIModule import APIModule
from Homevee.Item.Room import Room
from Homevee.Item.Status import *
from Homevee.Manager.RoomManager import RoomManager

ACTION_KEY_GET_ROOMS = "getrooms"
ACTION_KEY_ADD_EDIT_ROOM = "addeditroom"
ACTION_KEY_DELETE_ROOM = "deleteroom"
ACTION_KEY_MOVE_ITEMS_AND_DELETE_OLD_ROOM = "moveitemsanddeleteoldroom"
ACTION_KEY_DELETE_ROOM_WITH_ITEMS = "deleteroomwithitems"

class RoomAPIModule(APIModule):
    def __init__(self):
        super(RoomAPIModule, self).__init__()
        self.room_manager = RoomManager()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_GET_ROOMS: self.get_rooms,
            ACTION_KEY_ADD_EDIT_ROOM: self.add_edit_room,
            ACTION_KEY_DELETE_ROOM: self.delete_room,
            ACTION_KEY_MOVE_ITEMS_AND_DELETE_OLD_ROOM: self.move_items_and_delete_old_room,
            ACTION_KEY_DELETE_ROOM_WITH_ITEMS: self.delete_room_with_items
        }
        return mappings

    def get_rooms(self, user, request, db) -> Status:
        rooms = self.room_manager.get_rooms(user, db)
        return Status(type=STATUS_OK, data={'rooms': Room.list_to_dict(rooms)})

    def add_edit_room(self, user, request, db) -> Status:
        self.room_manager.add_edit_room(user, request['roomname'], request['location'], request['icon'], db)
        return Status(type=STATUS_OK)

    def delete_room(self, user, request, db) -> Status:
        self.room_manager.delete_room(user, request['location'], db)
        return Status(type=STATUS_OK)

    def move_items_and_delete_old_room(self, user, request, db) -> Status:
        self.room_manager.move_items_and_delete_old_room(user, request['oldroom'], request['newroom'], db)
        return Status(type=STATUS_OK)

    def delete_room_with_items(self, user, request, db) -> Status:
        self.room_manager.delete_room_with_items(user, request['location'], db)
        return Status(type=STATUS_OK)