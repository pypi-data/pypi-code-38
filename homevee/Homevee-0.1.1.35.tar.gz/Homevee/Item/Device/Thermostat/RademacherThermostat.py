import json
import traceback
import urllib.request

from Homevee.Exception import DatabaseSaveFailedException
from Homevee.Helper import Logger
from Homevee.Item.Device.Thermostat import Thermostat
from Homevee.Item.Gateway import *
from Homevee.Utils.Database import Database
from Homevee.Utils.DeviceTypes import RADEMACHER_THERMOSTAT


class RademacherThermostat(Thermostat):
    def __init__(self, name, icon, location, id=None, temp=None):
        super(RademacherThermostat, self).__init__(name, icon, location, id=id, temp=temp)

    def get_device_type(self):
        return RADEMACHER_THERMOSTAT

    def delete(self, db: Database = None):
        if db is None:
            db = Database()
        try:
            db.delete("DELETE FROM HOMEPILOT_THERMOSTATS WHERE ID == :id", {'id': self.id})
            return True
        except:
            return False

    def get_min_max(self):
        return 4, 28

    def save(self, db: Database = None):
        if db is None:
            db = Database()
        try:
            db.insert("""INSERT OR IGNORE INTO HOMEPILOT_THERMOSTATS (ID, NAME, ICON, LAST_TEMP, ROOM) VALUES 
                                        (:id, :name, :icon, :last_temp, :room)""",
                              {'id': self.id, 'name': self.name, 'icon': self.icon,
                               'last_temp': self.temp, 'room': self.location})
            # update
            db.update("""UPDATE OR IGNORE HOMEPILOT_THERMOSTATS SET NAME = :name, ICON = :icon,
                                        LAST_TEMP = :last_temp, ROOM = :room WHERE ID = :id""",
                              {'name': self.name, 'icon': self.icon, 'last_temp': self.temp,
                               'room': self.location, 'id': self.id})

                # TODO add generated id to object
        except:
            if(Logger.IS_DEBUG):
                traceback.print_exc()
            raise DatabaseSaveFailedException("Could not save homepilot-thermostat to database")

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
            gateway = Item.load_from_db(Gateway, RADEMACHER_HOMEPILOT)

            value = int(float(temp) * 10)

            url = "http://" + gateway.ip + "/deviceajax.do?cid=9&did=" + str(self.id) + "&goto=" + str(value) + "&command=0"

            response = urllib.request.urlopen(url).read()

            data = json.loads(response)

            if (data['status'] != 'uisuccess'):
                return False
            return True
        except:
            if Logger.IS_DEBUG:
                traceback.print_exc()
        return False

    @staticmethod
    def load_all_ids_from_db(ids, db: Database = None):
        if db is None:
            db = Database()
        return RademacherThermostat.load_all_from_db('SELECT * FROM HOMEPILOT_THERMOSTATS WHERE ID IN (%s)'
                                              % ','.join('?' * len(ids)), ids)

    @staticmethod
    def load_all_from_db(query, params, db: Database = None):
        if db is None:
            db = Database()
        items = []
        for result in db.select_all(query, params):
            item = RademacherThermostat(result['NAME'], result['ICON'], result['ROOM'], result['ID'],
                                 result['LAST_TEMP'])
            items.append(item)
        return items

    @staticmethod
    def load_all(db: Database):
        return RademacherThermostat.load_all_from_db('SELECT * FROM HOMEPILOT_THERMOSTATS', {})

    @staticmethod
    def create_from_dict(dict):
        try:
            name = dict['name']
            id = dict['id']
            location = dict['location']
            temp = dict['temp']
            icon = dict['icon']

            item = RademacherThermostat(name, icon, location, id, temp)

            return item

        except:
            raise InvalidParametersException("Invalid parameters for RademacherThermostat.create_from_dict()")