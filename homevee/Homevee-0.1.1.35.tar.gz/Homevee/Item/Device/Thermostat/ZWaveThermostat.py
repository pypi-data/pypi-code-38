import traceback

from Homevee.DeviceAPI.zwave.utils import do_zwave_request
from Homevee.Exception import DatabaseSaveFailedException, InvalidParametersException
from Homevee.Helper import Logger
from Homevee.Item.Device.Thermostat import Thermostat
from Homevee.Utils.Database import Database
from Homevee.Utils.DeviceTypes import ZWAVE_THERMOSTAT


class ZWaveThermostat(Thermostat):
    def __init__(self, name, icon, location, id=None, temp=None):
        super(ZWaveThermostat, self).__init__(name, icon, location, id=id, temp=temp)

    def get_device_type(self):
        return ZWAVE_THERMOSTAT

    def delete(self, db: Database = None):
        if db is None:
            db = Database()
        try:
            db.delete("DELETE FROM ZWAVE_THERMOSTATS WHERE ID == :id", {'id': self.id})
            return True
        except:
            return False

    def get_min_max(self):
        return 4, 40

    def save(self, db: Database = None):
        if db is None:
            db = Database()
        try:
            # insert
            db.insert("""INSERT OR IGNORE INTO ZWAVE_THERMOSTATS (THERMOSTAT_ID, NAME, ICON, VALUE, RAUM) VALUES 
                        (:id, :name, :icon, :last_temp, :room)""",
                        {'id': self.id, 'name': self.name, 'icon': self.icon,
                         'last_temp': self.temp, 'room': self.location})
            # update
            db.update("""UPDATE OR IGNORE ZWAVE_THERMOSTATS SET NAME = :name, ICON = :icon,
                        VALUE = :last_temp, RAUM = :room WHERE THERMOSTAT_ID = :id""",
                        {'name': self.name, 'icon': self.icon, 'last_temp': self.temp,
                        'room': self.location, 'id': self.id})

                # TODO add generated id to object
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
            result = do_zwave_request("/ZAutomation/api/v1/devices/" + str(self.id)
                                      + "/command/exact?level=" + str(temp),db)
            if result is not None and result['code'] == 200:
                return True
            else:
                return False
        except:
            if(Logger.IS_DEBUG):
                traceback.print_exc()
            return False

    @staticmethod
    def load_all_ids_from_db(ids, db: Database = None):
        if db is None:
            db = Database()
        return ZWaveThermostat.load_all_from_db('SELECT * FROM MAX_THERMOSTATS WHERE ID IN (%s)'
                                              % ','.join('?' * len(ids)), ids)

    @staticmethod
    def load_all_from_db(query, params, db: Database = None):
        if db is None:
            db = Database()
        items = []
        for result in db.select_all(query, params):
            item = ZWaveThermostat(result['NAME'], result['ICON'], result['RAUM'], result['THERMOSTAT_ID'],
                                 result['VALUE'])
            items.append(item)
        return items

    @staticmethod
    def load_all(db: Database = None):
        if db is None:
            db = Database()
        return ZWaveThermostat.load_all_from_db('SELECT * FROM ZWAVE_THERMOSTATS', {}, db)

    @staticmethod
    def create_from_dict(dict):
        try:
            name = dict['name']
            id = dict['id']
            location = dict['location']
            temp = dict['temp']
            icon = dict['icon']

            item = ZWaveThermostat(name, icon, location, id, temp)

            return item

        except:
            raise InvalidParametersException("Invalid parameters for ZWaveThermostat.create_from_dict()")