from Homevee.APIModule import APIModule
from Homevee.Item.ShoppingListItem import ShoppingListItem
from Homevee.Item.Status import *
from Homevee.Manager.ShoppingListManager import ShoppingListManager

ACTION_KEY_GET_SHOPPING_LIST = "getshoppinglist"
ACTION_KEY_ADD_EDIT_SHOPPING_LIST_ITEM = "addeditshoppinglistitem"
ACTION_KEY_DELETE_SHOPPING_LIST_ITEM = "deleteshoppinglistitem"

class ShoppingListAPIModule(APIModule):
    def __init__(self):
        super(ShoppingListAPIModule, self).__init__()
        self.shopping_list_manager = ShoppingListManager()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_GET_SHOPPING_LIST: self.get_shopping_list,
            ACTION_KEY_ADD_EDIT_SHOPPING_LIST_ITEM: self.add_edit_shopping_list_item,
            ACTION_KEY_DELETE_SHOPPING_LIST_ITEM: self.delete_shopping_list_item
        }

        return mappings

    def get_shopping_list(self, user, request, db):
        data = self.shopping_list_manager.get_shopping_list(user, db)
        return Status(type=STATUS_OK, data={'items': ShoppingListItem.list_to_dict(data)})

    def add_edit_shopping_list_item(self, user, request, db):
        data = self.shopping_list_manager.add_edit_shopping_list_item(user, request['id'],
                                                                       request['amount'], request['name'], db)
        return Status(type=STATUS_OK, data=data)

    def delete_shopping_list_item(self, user, request, db):
        data = self.shopping_list_manager.delete_shopping_list_item(user, request['id'], db)
        return Status(type=STATUS_OK, data=data)