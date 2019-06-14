from Homevee.Exception import DatabaseSaveFailedException, InvalidParametersException
from Homevee.Item import Item
from Homevee.Utils.Database import Database


class Person(Item):
    def __init__(self, name, nickname, phone_number, address, birthdate, longitude, latitude, id=None):
        super(Person, self).__init__()
        self.name = name
        self.nickname = nickname
        self.phone_number = phone_number
        self.address = address
        self.birthdate = birthdate
        self.longitude = longitude
        self.latitude = latitude
        self.id = id

    def delete(self, db: Database = None):
        if db is None:
            db = Database()
        try:
            db.delete("DELETE FROM PEOPLE_DATA WHERE ID == :id", {'id': self.id})
            return True
        except:
            return False

    def save(self, db: Database = None):
        if db is None:
            db = Database()
        try:
            if (self.id is None or self.id == ""):
                new_id = db.insert("""INSERT INTO PEOPLE_DATA (NAME, NICKNAME, PHONE_NUMBER, ADDRESS, BIRTHDATE, LONGITUDE, 
                LATITUDE) VALUES (:name, :nickname, :phone_number, :address, :birthdate, :longitude, :latitude)""",
                            {'name': self.name, 'nickname': self.nickname, 'phone_number': self.phone_number,
                             'address': self.address, 'birthdate': self.birthdate, 'longitude': self.longitude,
                             'latitude': self.latitude})
                self.id = new_id

            # update
            else:
                db.update("""UPDATE PEOPLE_DATA SET NAME = :name, NICKNAME = :nickname, PHONE_NUMBER = :phone_number,
                 ADDRESS = :address, BIRTHDATE = :birthdate, LONGITUDE = :longitude, LATITUDE = :latitude WHERE ID = :id""",
                                {'name': self.name, 'nickname': self.nickname, 'phone_number': self.phone_number,
                                 'address': self.address, 'birthdate': self.birthdate, 'longitude': self.longitude,
                                 'latitude': self.latitude, 'id': self.id})
                #TODO add generated id to object
        except:
            raise DatabaseSaveFailedException("Could not save event to database")

    def build_dict(self):
        dict = {
            'id': self.id,
            'name': self.name,
            'nickname': self.nickname,
            'phone_number': self.phone_number,
            'address': self.address,
            'birthdate': self.birthdate,
            'longitude': self.longitude,
            'latitude': self.latitude
        }
        return dict

    @staticmethod
    def load_all_from_db(query, params, db: Database = None):
        if db is None:
            db = Database()
        items = []
        for result in db.select_all(query, params):
            item = Person(result['NAME'], result['NICKNAME'], result['PHONE_NUMBER'], result['ADDRESS'], result['BIRTHDATE'], result['LONGITUDE'], result['LATITUDE'], result['ID'])
            items.append(item)
        return items

    @staticmethod
    def load_all_ids_from_db(ids, db: Database = None):
        if db is None:
            db = Database()
        return Person.load_all_from_db('SELECT * FROM PEOPLE_DATA WHERE ID IN (%s)'
                                              % ','.join('?' * len(ids)), ids, db)

    @staticmethod
    def load_all(db: Database):
        return Person.load_all_from_db('SELECT * FROM PEOPLE_DATA', {}, db)

    @staticmethod
    def create_from_dict(dict):
        try:
            id = dict['id']
            name = dict['name']
            nickname = dict['nickname']
            phone_number = dict['phone_number']
            address = dict['address']
            birthdate = dict['birthdate']
            latitude = dict['latitude']
            longitude = dict['longitude']

            item = Person(name, nickname, phone_number, address, birthdate, longitude, latitude, id)

            return item
        except:
            raise InvalidParametersException("Person.create_from_dict(): invalid dict")