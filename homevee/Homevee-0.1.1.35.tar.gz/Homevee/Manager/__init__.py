from abc import abstractmethod
from sqlite3 import Row
from typing import Type, List

from Homevee.Exception import NoPermissionException
from Homevee.Item import Item
from Homevee.Item.Status import Status, STATUS_ERROR, STATUS_OK
from Homevee.Item.User import User
from Homevee.Utils.Database import Database


class Manager():
    def __init__(self):
        return

    def api_add_edit(self, user: User, item: Type[Item], db: Database = None) -> Status:
        """
        Saves the given item and returns the status object of the transaction
        :param user: the user trying to do the action
        :param item: the item
        :param db: the database connection
        :return: the status
        """
        if not self.check_permission(user, item):
            raise NoPermissionException()
        
        if self.add_edit(item, db):
            return Status(type=STATUS_ERROR)
        else:
            return Status(type=STATUS_OK)
        
    def api_delete(self, user: User, item: Type[Item], db: Database = None) -> Status:
        """
        Deletes the given item and returns the status object of the transaction
        :param user: the user trying to do the action
        :param item: the item
        :param db: the database connection
        :return: the status
        """
        if not self.check_permission(user, item):
            raise NoPermissionException()
        
        if self.delete(item, db):
            return Status(type=STATUS_ERROR)
        else:
            return Status(type=STATUS_OK)

    def api_get_all(self, user: User, db: Database = None) -> list:
        """
        Gets all items (the user is allowed to manipulate) and returns them as a dict list
        :param user: the user trying to get all items
        :param db: the database connection
        :return: the list of dicts
        """
        all_items = self.get_all(db)

        output_items = []

        for item in all_items:
            if self.check_permission(user, item):
                output_items.append(item)

        return self.get_dict_list_from_item_list(all_items)

    def api_find_by_id(self, user: User, id: int, db: Database = None) -> dict:
        """
        Returns a single item identified by an id as a dict if the user is allowed to
        :param user: the user
        :param id: the id if the item to search
        :param db: the database connection
        :return: the dict of the item
        """
        item = self.find_by_id(id, db)

        if item is None:
            return None

        if self.check_permission(user, item):
            return None

        return self.get_dict_from_item(item)

    def add_edit(self, item: Type[Item], db: Database = None) -> bool:
        """
        Saves the given item and creates it if it does not exist yes
        :param item: the item
        :param db: the database connection
        :return: boolean if successful
        """
        if self.item_exists(item, db):
            return self.update(item, db)
        else:
            return self.create(item, db)

    def find_by_query(self, query: str, params: dict, db: Database = None) -> List[Type[Item]]:
        """
        Finds items identified by the given query
        :param query: the sql query
        :param params: the params-dict
        :param db: the database connection
        :return: the list of found items
        """
        if db is None:
            db = Database()

        items = []

        results = db.select_all(query, params)

        for result in results:
            items.append(self.create_item_from_db_result(result))

        return items

    def find_one_by_query(self, query: str, params: dict, db: Database = None) -> Type[Item]:
        """
        Finds a single item identified by the given query
        :param query: the sql query
        :param params: the params-dict
        :param db: the database connection
        :return: the found item
        """
        if db is None:
            db = Database()

        items = []

        results = db.select_all(query, params)

        for result in results:
            items.append(self.create_item_from_db_result(result))

        if len(items) > 0:
            return items[0]
        else:
            return None

    def get_dict_list_from_item_list(self, list: List[Type[Item]]) -> list:
        """
        Creates a dict list from a given list of items
        :param list: the list of dicts
        :return: the list of items
        """
        output = []
        for item in list:
            output.append(self.get_dict_from_item(item))
        return output

    def create_item_list_from_dict_list(self, list: list) -> List[Type[Item]]:
        """
        Creates a item list from a given list of dicts
        :param list: the list of items
        :return: the list of dicts
        """
        items = []
        for dict in list:
            items.append(self.construct_item_from_dict(dict))
        return items

    def get_dict_from_item(self, item: Type[Item]) -> dict:
        """
        Builds a dict from the given item
        :param item: the item
        :return: the built dict
        """
        return item.get_dict()

    @abstractmethod
    def create_item_from_db_result(self, result: Row) -> Type[Item]:
        """
        Creates an item from the database result row
        :param result: the database result row
        :return: the created item
        """
        raise NotImplementedError

    @abstractmethod
    def item_exists(self, item: Type[Item], db: Database) -> bool:
        """
        Checks whether the given item already exists or not
        :param item: the item
        :param db: the database connection
        :return: true if item exists, false if not
        """
        raise NotImplementedError

    @abstractmethod
    def create(self, item: Type[Item], db: Database) -> bool:
        """
        Creates the given item
        :param item: the item
        :param db: the database connection
        :return: boolean if successful
        """
        raise NotImplementedError

    @abstractmethod
    def update(self, item: Type[Item], db: Database) -> bool:
        """
        Updates the given item
        :param item: the item
        :param db: the database connection
        :return: boolean if successful
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, item: Type[Item], db: Database) -> bool:
        """
        Deletes the given item
        :param item: the item
        :param db: the database connection
        :return: boolean if successful
        """
        raise NotImplementedError

    @abstractmethod
    def get_all(self, db: Database) -> List[Type[Item]]:
        """
        Gets all existing items
        :return: the list of items
        """
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, id: int, db: Database) -> Type[Item]:
        """
        Finds a single item identified by the given id
        :param id: the id
        :param db: the database connection
        :return: the found item
        """
        raise NotImplementedError()

    @abstractmethod
    def construct_item_from_dict(self, dict: dict) -> Type[Item]:
        """
        Construct an item out of a given dict
        :param dict: the dict
        :return: the constructed item
        """
        raise NotImplementedError()

    @abstractmethod
    def check_permission(self, user: User, item: Type[Item]) -> bool:
        """
        Checks if the given user is allowed to manipulate the item
        :param user: the user
        :param item: the item
        :return: boolean if user is allowed
        """
        raise NotImplementedError