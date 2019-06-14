from Homevee.APIModule import APIModule
from Homevee.Item.Status import *
from Homevee.Manager.HeatingSchemeManager import HeatingSchemeManager

ACTION_KEY_ADD_EDIT_HEATING_SCHEME_ITEM = "addeditheatingschemeitem"
ACTION_KEY_DELETE_HEATING_SCHEME_ITEM = "deleteheatingschemeitem"
ACTION_KEY_GET_HEATING_SCHEME_ITEMS = "getheatingschemeitems"
ACTION_KEY_SET_HEATING_SCHEME_ITEM_ACTIVE = "setheatingschemeitemactive"
ACTION_KEY_GET_HEATING_SCHEME_ITEM_DATA = "getheatingschemeitemdata"
ACTION_KEY_SET_HEATING_SCHEME_ACTIVE = "setheatingschemeactive"
ACTION_KEY_IS_HEATING_SCHEME_ACTIVE = "isheatingschemeactive"

class HeatingSchemeAPIModule(APIModule):
    def __init__(self):
        super(HeatingSchemeAPIModule, self).__init__()
        self.heating_scheme_manager = HeatingSchemeManager()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_ADD_EDIT_HEATING_SCHEME_ITEM: self.add_edit_heating_scheme_item,
            ACTION_KEY_DELETE_HEATING_SCHEME_ITEM: self.delete_heating_scheme_item,
            ACTION_KEY_GET_HEATING_SCHEME_ITEMS: self.get_heating_scheme_items,
            ACTION_KEY_SET_HEATING_SCHEME_ITEM_ACTIVE: self.set_heating_scheme_item_active,
            ACTION_KEY_GET_HEATING_SCHEME_ITEM_DATA: self.get_heating_scheme_item_data,
            ACTION_KEY_SET_HEATING_SCHEME_ACTIVE: self.set_heating_scheme_active,
            ACTION_KEY_IS_HEATING_SCHEME_ACTIVE: self.is_heating_scheme_active
        }

        return mappings

    def add_edit_heating_scheme_item(self, user, request, db):
        data = self.heating_scheme_manager.add_edit_heating_scheme_item(user, request['id'], request['time'],
                                                                           request['value'],
                                                                           request['active'], request['days'],
                                                                           request['data'], db)
        return Status(type=STATUS_OK, data=data)

    def delete_heating_scheme_item(self, user, request, db):
        data = self.heating_scheme_manager.delete_heating_scheme_item(user, request['id'], db)
        return Status(type=STATUS_OK, data=data)

    def get_heating_scheme_items(self, user, request, db):
        data = self.heating_scheme_manager.get_heating_scheme_items(user, request['day'], request['rooms'], db)
        return Status(type=STATUS_OK, data={'items': data})

    def set_heating_scheme_item_active(self, user, request, db):
        self.heating_scheme_manager.set_heating_scheme_item_active(user, request['id'], request['active'], db)
        return Status(type=STATUS_OK)

    def get_heating_scheme_item_data(self, user, request, db):
        data = self.heating_scheme_manager.get_heating_scheme_item_data(user, request['id'], db)
        return Status(type=STATUS_OK, data=data)

    def set_heating_scheme_active(self, user, request, db):
        self.heating_scheme_manager.set_heating_scheme_active(user, request['active'], db)
        return Status(type=STATUS_OK)

    def is_heating_scheme_active(self, user, request, db):
        data = self.heating_scheme_manager.is_heating_scheme_active(user, db)
        return Status(type=STATUS_OK, data={'isactive': data})