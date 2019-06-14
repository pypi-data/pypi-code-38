from Homevee.Exception import DatabaseSaveFailedException, InvalidParametersException
from Homevee.Item import Item
from Homevee.Utils.Database import Database

class APIKey(Item):
    def __init__(self, name, key, id=None):
        super(APIKey, self).__init__()
        self.id = id
        self.key = key
        self.name = name

    def delete(self, db: Database = None):
        if db is None:
            db = Database()
        try:
            db.delete("DELETE FROM API_KEYS WHERE ID == :id", {'id': self.id})
            return True
        except:
            return False

    def save(self, db: Database = None):
        if db is None:
            db = Database()
        try:
            if (self.id is None or self.id == ""):
                new_id = db.insert("""INSERT INTO API_KEYS (SERVICE_NAME, API_KEY) VALUES (:name, :key)""",
                            {'name': self.name, 'key': self.key})
                self.id = new_id

            # update
            else:
                db.update("""UPDATE API_KEYS SET SERVICE_NAME = :name, API_KEY = :key WHERE ID = :id""",
                                {'name': self.name, 'key': self.key, 'id': self.id})
                #TODO add generated id to object
        except:
            raise DatabaseSaveFailedException("Could not save event to database")

    def build_dict(self):
        dict = {
            'id': self.id,
            'name': self.name,
            'key': self.key,
        }
        return dict

    @staticmethod
    def load_all_from_db(query, params, db: Database = None):
        if db is None:
            db = Database()
        items = []
        for result in db.select_all(query, params):
            item = APIKey(result['SERVICE_NAME'], result['API_KEY'], result['ID'])
            items.append(item)
        return items

    @staticmethod
    def load_all_ids_from_db(ids, db: Database = None):
        if db is None:
            db = Database()
        return APIKey.load_all_from_db('SELECT * FROM API_KEYS WHERE ID IN (%s)'
                                              % ','.join('?' * len(ids)), ids, db)

    @staticmethod
    def find_by_name(name, db: Database = None):
        if db is None:
            db = Database()
        results = APIKey.load_all_from_db('SELECT * FROM API_KEYS WHERE SERVICE_NAME = :name', {'name': name}, db)

        if len(results) > 0:
            return results[0]
        else:
            return None

    @staticmethod
    def load_all(db: Database):
        return APIKey.load_all_from_db('SELECT * FROM API_KEYS', {}, db)

    @staticmethod
    def create_from_dict(dict):
        try:
            id = dict['id']
            name = dict['name']
            key = dict['key']

            item = APIKey(name, key, id)

            return item
        except:
            raise InvalidParametersException("Person.create_from_dict(): invalid dict")