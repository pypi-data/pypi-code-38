from Homevee.Exception import InvalidParametersException, AbstractFunctionCallException, ItemNotFoundException
from Homevee.Item.Status import *
from Homevee.Utils.Database import Database


class Item():
    def __init__(self):
        pass

    def api_delete(self, db: Database = None) -> dict:
        """
        Deletes the object from the database
        :param db: the database connection
        :return: Status of the request
        """
        try:
            if self.delete(db):
                return Status(type=STATUS_OK).get_dict()
        except:
            pass
        return Status(type=STATUS_ERROR).get_dict()

    def api_save(self, db: Database = None) -> dict:
        """
        Saves the object to the database
        :param db: the database connection
        :return: Status of the request
        """
        try:
            self.save(db)
            return Status(type=STATUS_OK).get_dict()
        except:
            pass
        return Status(type=STATUS_ERROR).get_dict()

    def delete(self, db: Database = None):
        """
        Deletes the object from the database
        :param db: the database connection
        :return:
        """
        raise AbstractFunctionCallException("Item.delete() is abstract")

    def save(self, db: Database = None):
        if db is None:
            db = Database()
        """
        Saves the object to the database
        :param db: the database connection
        :return:
        """
        raise AbstractFunctionCallException("Item.save_to_db() is abstract")

    def build_dict(self) -> dict:
        """
        Generates a dict from the object
        :return: a dict of the object
        """
        raise AbstractFunctionCallException("Item.build_dict() is abstract")

    def get_dict(self, fields: list = None) -> dict:
        """
        Creates a dict from the object
        :param fields: list of fields to add to the object
        :return: a dict of the object
        """
        dict = self.build_dict()
        if (fields is None):
            return dict
        else:
            try:
                output_dict = {}
                for field in fields:
                    output_dict[field] = dict[field]
                return output_dict
            except:
                raise InvalidParametersException("InvalidParams given for get_dict()")

    @staticmethod
    def load_all_ids_from_db(ids: list, db: Database) -> list:
        """
        Retrieves items identified by the given ids from the database
        :param ids: the ids to retrieves items for
        :param db: the database connection
        :return: the found items
        """
        raise AbstractFunctionCallException("Item.load_all_ids_from_db() is abstract")

    @staticmethod
    def load_all_from_db(query, params, db: Database) -> list:
        """
        Loads all items identified by the given query and the params
        :param query: string of the SQL-query
        :param params: the params for the query
        :param db: the database connection
        :return: a list of found items
        """
        raise AbstractFunctionCallException("Item.load_all_from_db() is abstract")

    @staticmethod
    def load_from_db(module, id: int, db: Database = None):
        """
        Retrieves an item from the database
        :param module: the module to call the method on
        :param id: the id of the item to retrieve
        :param db: the database connection
        :return: the found item
        """
        items = module.load_all_ids_from_db([id], db)
        if ((len(items) == 0) or (str(items[0].id) != str(id))):
            raise ItemNotFoundException("Could not find id: " + id)
        else:
            return items[0]

    @staticmethod
    def create_from_dict(dict: dict):
        """
        Creates an item from the given dict
        :param dict: dict to create an item from
        :return: Item
        """
        raise AbstractFunctionCallException("Item.create_from_dict() is abstract")

    @staticmethod
    def list_to_dict(list: list) -> list:
        """
        Converts a list of items to a list of dicts of items
        :param list: list of items
        :return: list of dicts of items
        """
        data = []
        for item in list:
            data.append(item.get_dict())
        return data