import traceback

from pymax.cube import Cube

from Homevee.DeviceAPI import max_cube_control
from Homevee.Exception import DatabaseSaveFailedException
from Homevee.Helper import Logger
from Homevee.Item.Device.Thermostat import Thermostat
from Homevee.Item.Gateway import *
from Homevee.Utils.Database import Database
from Homevee.Utils.DeviceTypes import MAX_THERMOSTAT


class MaxThermostat(Thermostat):
    def __init__(self, name, icon, location, id=None, temp=None):
        super(MaxThermostat, self).__init__(name, icon, location, id=id, temp=temp)

    def get_device_type(self):
        return MAX_THERMOSTAT

    def delete(self, db: Database = None):
        if db is None:
            db = Database()
        try:
            db.delete("DELETE FROM MAX_THERMOSTATS WHERE ID == :id", {'id': self.id})
            return True
        except:
            return False

    def get_min_max(self):
        return 0, 30

    def save(self, db: Database = None):
        if db is None:
            db = Database()
        try:
            # insert
            db.insert("""INSERT OR IGNORE INTO MAX_THERMOSTATS (ID, NAME, ICON, LAST_TEMP, ROOM) VALUES 
                        (:id, :name, :icon, :last_temp, :room)""",
                        {'id': self.id, 'name': self.name, 'icon': self.icon,
                        'last_temp': self.temp, 'room': self.location})
            # update
            db.update("""UPDATE OR IGNORE MAX_THERMOSTATS SET NAME = :name, ICON = :icon,
                        LAST_TEMP = :last_temp, ROOM = :room WHERE ID = :id""",
                        {'name': self.name, 'icon': self.icon, 'last_temp': self.temp,
                        'room': self.location, 'id': self.id})
                #TODO add generated id to object
        except:
            if(Logger.IS_DEBUG):
                traceback.print_exc()
            raise DatabaseSaveFailedException("Could not save max-thermostat to database")

    def build_dict(self):
        dict = {
            'name': self.name,
            'icon': self.icon,
            'id': self.id,
            'temp': self.temp,
            'location': self.location
        }
        return dict

    def update_temp(self, temp, db: Database = None):
        if db is None:
            db = Database()
        try:
            gateway = Item.load_from_db(Gateway, MAX_CUBE)

            data = max_cube_control.get_device_data(gateway.ip, self.id)

            # temperatur berechnen
            tempVal = temp

            with Cube(gateway.ip) as cube:
                result = cube.set_mode_manual(data['room'], data['addr'], tempVal)

            return True

        except:
            if(Logger.IS_DEBUG):
                traceback.print_exc()
            return False

    @staticmethod
    def load_all_ids_from_db(ids, db: Database = None):
        if db is None:
            db = Database()
        return MaxThermostat.load_all_from_db('SELECT * FROM MAX_THERMOSTATS WHERE ID IN (%s)'
                                              % ','.join('?' * len(ids)), ids, db)

    @staticmethod
    def load_all_from_db(query, params, db: Database = None):
        if db is None:
            db = Database()
        items = []
        for result in db.select_all(query, params):
            item = MaxThermostat(result['NAME'], result['ICON'], result['RAUM'], result['ID'],
                                 result['LAST_TEMP'])
            items.append(item)
        return items

    @staticmethod
    def load_all(db: Database):
        return MaxThermostat.load_all_from_db('SELECT * FROM MAX_THERMOSTATS', {}, db)

    @staticmethod
    def create_from_dict(dict):
        try:
            name = dict['name']
            id = dict['id']
            location = dict['location']
            temp = dict['temp']
            icon = dict['icon']

            item = MaxThermostat(name, icon, location, id, temp)

            return item

        except:
            raise InvalidParametersException("Invalid parameters for MaxThermostat.create_from_dict()")