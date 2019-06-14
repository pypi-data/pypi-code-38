from Homevee.Exception import InvalidParametersException, DatabaseSaveFailedException
from Homevee.Item import Item
from Homevee.Utils.Database import Database


class Room(Item):
    def __init__(self, name, icon, id=None):
        super(Room, self).__init__()
        self.id = id
        self.name = name
        self.icon = icon

        self.room_data = None

    def get_room_data(self, db: Database = None):
        if db is None:
            db = Database()
        if(self.room_data is None):
            room_data = None #TODO load room data
            self.room_data = room_data
        return self.room_data

    def delete(self, db: Database = None):
        if db is None:
            db = Database()
        #TODO implement room deletion
        return False

    def save(self, db: Database = None):
        if db is None:
            db = Database()
        try:
            #insert
            if(self.id is None or self.id == ""):
                db.insert("INSERT INTO ROOMS (NAME, ICON) VALUES (:name, :icon)",
                            {'name': self.name, 'icon': self.icon})
            #update
            else:
                db.update("UPDATE ROOMS SET NAME = :name, ICON = :icon WHERE LOCATION = :id",
                            {'name': self.name, 'icon': self.icon, 'id': self.id})
                    # TODO add generated id to object
        except:
            raise DatabaseSaveFailedException("Could not save room to database")

    def get_dict(self, fields=None):
        dict = {
            'id': self.id,
            'name': self.name,
            'icon': self.icon
        }

        if(fields is None):
            return dict
        else:
            try:
                output_dict = {}

                for field in fields:
                    output_dict[field] = dict[field]

                return output_dict
            except:
                raise InvalidParametersException("InvalidParams given for Room.get_dict()")

    @staticmethod
    def load_all_ids_from_db(ids, db: Database = None):
        if db is None:
            db = Database()
        return Room.load_all_from_db('SELECT * FROM ROOMS WHERE LOCATION IN (%s)' % ','.join('?'*len(ids)), ids)

    @staticmethod
    def load_all_from_db(query, params, db: Database = None):
        if db is None:
            db = Database()
        items = []
        for result in db.select_all(query, params):
            item = Room(result['NAME'], result['ICON'], result['LOCATION'])
            items.append(item)
        return items

    @staticmethod
    def get_name_by_id(id, db: Database = None):
        if db is None:
            db = Database()
        room = Item.load_from_db(Room, id, db)
        return room.name

    @staticmethod
    def load_all(db: Database):
        if db is None:
            db = Database()

        return Room.load_all_from_db('SELECT * FROM ROOMS', {}, db)

    @staticmethod
    def create_from_dict(dict):
        try:
            id = dict['id']
            name = dict['name']
            icon = dict['icon']
            room = Room(name, icon, id)
            return room
        except:
            raise InvalidParametersException("Room.create_from_dict(): invalid dict")