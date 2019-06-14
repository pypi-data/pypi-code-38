import urllib.request

from Homevee.Exception import *
from Homevee.Item import Item
from Homevee.Item.Device.Switch import Switch
from Homevee.Item.Gateway import Gateway, FUNKSTECKDOSEN_CONTROLLER
from Homevee.Utils.Database import Database
from Homevee.Utils.DeviceTypes import FUNKSTECKDOSE


class Funksteckdose(Switch):
    def __init__(self, name, icon, location, home_code, socket_number, id=None, mode=False):
        super(Funksteckdose, self).__init__(name, icon, location, id=id, mode=mode)
        self.home_code = home_code
        self.socket_number = socket_number

    def get_device_type(self):
        return FUNKSTECKDOSE

    def delete(self, db: Database = None):
        if db is None:
            db = Database()
        try:
            db.delete("DELETE FROM FUNKSTECKDOSEN WHERE DEVICE == :id", {'id': self.id})
            return True
        except:
            return False

    def save(self, db: Database = None):
        if db is None:
            db = Database()
        try:
            #insert
            if(self.id is None or self.id == ""):
                db.insert("INSERT INTO FUNKSTECKDOSEN (ROOM, NAME, ICON, HAUSCODE, STECKDOSENNNUMMER) "
                            "VALUES (:location, :name, :icon, :home_code, :socket_number)",
                            {'location': self.location, 'name': self.name, 'icon': self.icon,
                             'home_code': self.home_code, 'socket_number': self.socket_number})
            #update
            else:
                db.update("UPDATE FUNKSTECKDOSEN SET ROOM = :location, NAME = :name, ICON = :icon,"
                            "HAUSCODE = :home_code, STECKDOSENNUMMER = :socket_number, ZUSTAND = :mode"
                            "WHERE DEVICE = :id",
                            {'location': self.location, 'name': self.name, 'icon': self.icon,
                             'home_code': self.home_code, 'socket_number': self.socket_number,
                             'mode': self.mode, 'id': self.id})
                    # TODO add generated id to object
        except:
            raise DatabaseSaveFailedException("Could not save room to database")

    def build_dict(self):
        dict = {
            'name': self.name,
            'icon': self.icon,
            'home_code': self.home_code,
            'socket_number': self.socket_number,
            'id': self.id,
            'mode': self.mode,
            'location': self.location
        }
        return dict

    def update_mode(self, mode, db: Database = None):
        if db is None:
            db = Database()
        try:
            gateway = Item.load_from_db(Gateway, FUNKSTECKDOSEN_CONTROLLER)

            url = 'http://' + str(gateway.ip) + '/funksteckdose.php?hauscode=' + str(self.home_code) + \
                  '&steckdosennummer=' + str(self.socket_number) + "&zustand=" + str(mode)
            #Logger.log(url)
            result = urllib.request.urlopen(url)

            return True
        except:
            return False

    @staticmethod
    def load_all_ids_from_db(ids, db: Database = None):
        if db is None:
            db = Database()
        return Funksteckdose.load_all_from_db('SELECT * FROM FUNKSTECKDOSEN WHERE DEVICE IN (%s)'
                                              % ','.join('?' * len(ids)), ids)

    @staticmethod
    def load_all_from_db(query, params, db: Database = None):
        if db is None:
            db = Database()
        items = []
        for result in db.select_all(query, params):
            item = Funksteckdose(result['NAME'], result['ICON'], result['ROOM'], result['HAUSCODE'],
                                 result['STECKDOSENNUMMER'], result['DEVICE'], result['ZUSTAND'])
            items.append(item)
        return items

    @staticmethod
    def load_all(db: Database):
        return Funksteckdose.load_all_from_db('SELECT * FROM FUNKSTECKDOSEN', {})

    @staticmethod
    def create_from_dict(dict):
        try:
            name = dict['name']
            id = dict['id']
            location = dict['location']
            home_code = dict['home_code']
            socket_number = dict['socket_number']
            mode = dict['mode']
            icon = dict['icon']

            funksteckdose = Funksteckdose(name, icon, location, home_code, socket_number, id, mode)

            return funksteckdose

        except:
            raise InvalidParametersException("Invalid parameters for Funksteckdose.create_from_dict()")