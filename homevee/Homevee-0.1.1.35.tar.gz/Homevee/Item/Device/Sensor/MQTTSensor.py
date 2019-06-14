from Homevee.Exception import *
from Homevee.Item.Device.Sensor import Sensor
from Homevee.Utils.Database import Database
from Homevee.Utils.DeviceTypes import MQTT_SENSOR


class MQTTSensor(Sensor):
    def __init__(self, name, icon, location, save_data, sensor_type, mqtt_device_id, mqtt_value_id, id=None, value=None):
        super(MQTTSensor, self).__init__(name, icon, location, save_data, sensor_type, id=id, value=value)
        self.mqtt_device_id = mqtt_device_id
        self.mqtt_value_id = mqtt_value_id

    def get_device_type(self) -> str:
        return MQTT_SENSOR

    def delete(self, db: Database = None):
        if db is None:
            db = Database()
        try:
            db.delete("DELETE FROM MQTT_SENSORS WHERE ID == :id", {'id': self.id})
            return True
        except:
            return False

    def save(self, db: Database = None):
        if db is None:
            db = Database()
        try:
            #insert
            if(self.id is None or self.id == ""):
                db.insert("INSERT INTO MQTT_SENSORS (ROOM, NAME, ICON, SAVE_DATA,"
                            "TYPE, LAST_VALUE, DEVICE_ID, VALUE_ID) VALUES (:location, :name, :icon, :save_data,"
                            ":sensor_type, :mqtt_device_id, :mqtt_value_id)",
                            {'location': self.location, 'name': self.name, 'icon': self.icon,
                             'save_data': self.save_data, 'sensor_type': self.sensor_type,
                             'mqtt_device_id': self.mqtt_device_id, 'mqtt_value_id': self.mqtt_value_id,})
            #update
            else:
                db.update("UPDATE MQTT_SENSORS SET ROOM = :location, NAME = :name, ICON = :icon,"
                            "SAVE_DATA = :save_data, TYPE = :sensor_type, DEVICE_ID = :mqtt_device_id, "
                                "VALUE_ID = :mqtt_value_id, LAST_VALUE = :value WHERE ID = :id",
                            {'location': self.location, 'name': self.name, 'icon': self.icon,
                             'save_data': self.save_data, 'sensor_type': self.sensor_type,
                             'mqtt_device_id': self.mqtt_device_id, 'mqtt_value_id': self.mqtt_value_id,
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
            'sensor_type': self.sensor_type,
            'mqtt_device_id': self.mqtt_device_id,
            'mqtt_value_id': self.mqtt_value_id
        }
        return dict

    @staticmethod
    def load_all_ids_from_db(ids, db: Database = None):
        if db is None:
            db = Database()
        return MQTTSensor.load_all_from_db('SELECT * FROM MQTT_SENSORS WHERE ID IN (%s)'
                                              % ','.join('?' * len(ids)), ids)

    @staticmethod
    def load_all_from_db(query, params, db: Database = None):
        if db is None:
            db = Database()
        items = []
        for result in db.select_all(query, params):
            item = MQTTSensor(result['NAME'], result['ICON'], result['ROOM'], result['SAVE_DATA'],
                                 result['TYPE'], result['DEVICE_ID'], result['VALUE_ID'],
                              result['ID'], result['LAST_VALUE'])
            items.append(item)
        return items

    @staticmethod
    def load_all(db: Database):
        if db is None:
            db = Database()
        return MQTTSensor.load_all_from_db('SELECT * FROM MQTT_SENSORS', {})

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
            mqtt_device_id = dict['mqtt_device_id']
            mqtt_value_id = dict['mqtt_value_id']

            item = MQTTSensor(name, icon, location, save_data, sensor_type, mqtt_device_id, mqtt_value_id, id, value)

            return item
        except:
            raise InvalidParametersException("Invalid parameters for MQTTSensor.create_from_dict()")