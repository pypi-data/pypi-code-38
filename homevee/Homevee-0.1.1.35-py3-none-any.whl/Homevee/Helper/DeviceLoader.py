from Homevee.Exception import InvalidParametersException, NoSuchTypeException
from Homevee.Item import Item
from Homevee.Item.Device.Sensor.MQTTSensor import MQTTSensor
from Homevee.Item.Device.Sensor.ZWaveSensor import ZWaveSensor
from Homevee.Item.Device.Switch.Funksteckdose import Funksteckdose
from Homevee.Item.Device.Switch.URLSwitch import URLSwitch
from Homevee.Item.Device.Thermostat.MaxThermostat import MaxThermostat
from Homevee.Item.Device.Thermostat.RademacherThermostat import RademacherThermostat
from Homevee.Item.Device.Thermostat.ZWaveThermostat import ZWaveThermostat
from Homevee.Utils.Database import Database
from Homevee.Utils.DeviceTypes import *


class DeviceLoader():
    def __init__(self):
        pass

    def load_devices(self, device_data: dict) -> list:
        """
        Loads devices identified by the device data dict
        :param device_data: dict of {'device_type': device_type, 'id': id}
        :return: list of devices
        """
        items = []
        db_con = Database()
        try:
            for data_item in device_data:
                id = data_item['id']
                if data_item['device_type'] == FUNKSTECKDOSE:
                    module = Funksteckdose
                elif data_item['device_type'] == URL_SWITCH:
                    module = URLSwitch
                elif data_item['device_type'] == MAX_THERMOSTAT:
                    module = MaxThermostat
                elif data_item['device_type'] == RADEMACHER_THERMOSTAT:
                    module = RademacherThermostat
                elif data_item['device_type'] == ZWAVE_THERMOSTAT:
                    module = ZWaveThermostat
                elif data_item['device_type'] == ZWAVE_SENSOR:
                    module = ZWaveSensor
                elif data_item['device_type'] == MQTT_SENSOR:
                    module = MQTTSensor
                else:
                    raise NoSuchTypeException("unkown type: "+data_item['device_type'])
                item = Item.load_from_db(module, id, db_con)
                items.append(item)
            return items
        except:
            raise InvalidParametersException("invalid params for DeviceLoader.load_devices()")
