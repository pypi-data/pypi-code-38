#!/usr/bin/python
# -*- coding: utf-8 -*-
from Homevee.Item import Item
from Homevee.Item.ShoppingListItem import ShoppingListItem
from Homevee.Utils.Database import Database

class ShoppingListManager:
    def __init__(self):
        return

    def get_shopping_list(self, user, db: Database = None):
        """
        Gets all shoppinglist-items from the database
        :param user: the calling user
        :param db: the databse connection
        :return: the list of dicts of items on the shopping list
        """
        if db is None:
            db = Database()
        items = ShoppingListItem.load_all(db)
        return items

    def add_edit_shopping_list_item(self, user, id, amount, name, db: Database = None):
        """
        Adds a new item to the shopping list
        :param user: the calling user
        :param id: the id of the item
        :param amount: the amount of the item
        :param name: the name of the item
        :param db: the database connection
        :return: the dict of the status object of the transaction
        """
        if db is None:
            db = Database()
        shopping_list_item = Item.load_from_db(ShoppingListItem, id, db)
        if shopping_list_item is None:
            shopping_list_item = ShoppingListItem(name, amount, id)
        else:
            shopping_list_item.amount = amount
            shopping_list_item.name = name

        return shopping_list_item.save(db)

    def delete_shopping_list_item(self, user, id, db: Database = None):
        """
        Deletes an item from the shopping list
        :param user: the calling user
        :param id: the id of the item to delete
        :param db: the database connection
        :return: the dict of status object of the transaction
        """
        if db is None:
            db = Database()
        item = Item.load_from_db(ShoppingListItem, id, db)
        return item.delete(db)