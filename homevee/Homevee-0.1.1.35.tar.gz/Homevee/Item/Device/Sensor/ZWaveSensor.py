from Homevee.Exception import *
from Homevee.Item.Device.Sensor import Sensor
from Homevee.Utils.Database import Database
from Homevee.Utils.DeviceTypes import ZWAVE_SENSOR


class ZWaveSensor(Sensor):
    def __init__(self, name, icon, location, save_data, sensor_type, id=None, value=None):
        super(ZWaveSensor, self).__init__(name, icon, location, save_data, sensor_type, id=id, value=value)

    def get_device_type(self):
        return ZWAVE_SENSOR

    def delete(self, db: Database = None):
        if db is None:
            db = Database()
        try:
            db.delete("DELETE FROM ZWAVE_SENSOREN WHERE ID == :id", {'id': self.id})
            return True
        except:
            return False

    def save(self, db: Database = None):
        if db is None:
            db = Database()
        try:
            #insert
            if(self.id is None or self.id == ""):
                db.insert("INSERT INTO ZWAVE_SENSOREN (RAUM, SHORTFORM, ICON, SAVE_DATA,"
                            "SENSOR_TYPE, VALUE) VALUES (:location, :name, :icon, :save_data,"
                            ":sensor_type)",
                            {'location': self.location, 'name': self.name, 'icon': self.icon,
                             'save_data': self.save_data, 'sensor_type': self.sensor_type})
            #update
            else:
                db.update("UPDATE ZWAVE_SENSOREN SET RAUM = :location, SHORTFORM = :name, ICON = :icon,"
                            "SAVE_DATA = :save_data, SENSOR_TYPE = :sensor_type, VALUE = :value"
                            "WHERE ID = :id",
                            {'location': self.location, 'name': self.name, 'icon': self.icon,
                             'save_data': self.save_data, 'sensor_type': self.sensor_type,
                             'value': self.value, 'id': self.id})
                    # TODO add generated id to object
        except:
            raise DatabaseSaveFailedException("Could not save room to database")

    def build_dict(self):
        dict = {
            'name': self.name,
            'icon': self.icon,
            'value': self.value,
            'id': self.id,
            'location': self.location,
            'save_data': self.save_data,
            'sensor_type': self.sensor_type
        }
        return dict

    @staticmethod
    def load_all_ids_from_db(ids, db: Database = None):
        if db is None:
            db = Database()
        return ZWaveSensor.load_all_from_db('SELECT * FROM ZWAVE_SENSOREN WHERE ID IN (%s)'
                                              % ','.join('?' * len(ids)), ids)

    @staticmethod
    def load_all_from_db(query, params, db: Database = None):
        if db is None:
            db = Database()
        items = []
        for result in db.select_all(query, params):
            item = ZWaveSensor(result['SHORTFORM'], result['ICON'], result['RAUM'], result['SAVE_DATA'],
                                 result['SENSOR_TYPE'], result['ID'], result['VALUE'])
            items.append(item)
        return items

    @staticmethod
    def load_all(db: Database):
        if db is None:
            db = Database()
        return ZWaveSensor.load_all_from_db('SELECT * FROM ZWAVE_SENSOREN', {})

    @staticmethod
    def create_from_dict(dict):
        try:
            name = dict['name']
            id = dict['id']
            location = dict['location']
            value = dict['value']
            icon = dict['icon']
            save_data = dict['save_data']
            sensor_type = dict['sensor_type']

            item = ZWaveSensor(name, icon, location, save_data, sensor_type, id, value)

            return item

        except:
            raise InvalidParametersException("Invalid parameters for ZWaveSensor.create_from_dict()")