from Homevee.APIModule import APIModule
from Homevee.Item.Status import *
from Homevee.Manager.PlaceManager import PlaceManager

ACTION_KEY_ADD_EDIT_PLACE = "addeditplace"
ACTION_KEY_GET_MY_PLACES = "getmyplaces"
ACTION_KEY_DELETE_PLACE = "deleteplace"

class PlaceAPIModule(APIModule):
    def __init__(self):
        super(PlaceAPIModule, self).__init__()
        self.place_manager = PlaceManager()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_ADD_EDIT_PLACE: self.add_edit_place,
            ACTION_KEY_GET_MY_PLACES: self.get_my_places,
            ACTION_KEY_DELETE_PLACE: self.delete_place
        }

        return mappings

    def add_edit_place(self, user, request, db):
        self.place_manager.add_edit_place(user, request['id'], request['name'],
                                                     request['address'], request['latitude'],
                                                     request['longitude'], db)
        return Status(type=STATUS_OK)

    def get_my_places(self, user, request, db):
        places = self.place_manager.get_my_places(user, db)
        return Status(type=STATUS_OK, data={'places':places})

    def delete_place(self, user, request, db):
        self.place_manager.delete_place(user, request['id'], db)
        return Status(type=STATUS_OK)