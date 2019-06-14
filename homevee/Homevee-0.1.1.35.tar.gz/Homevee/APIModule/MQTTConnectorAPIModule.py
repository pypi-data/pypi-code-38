from Homevee.APIModule import APIModule
from Homevee.Item.Status import *
from Homevee.Manager.MQTTConnectorManager import MQTTConnectorManager

ACTION_KEY_GENERATE_DEVICE_DATA = "generatedevicedata"
ACTION_KEY_SAVE_MQTT_DEVICE = "savemqttdevice"

class MQTTConnectorAPIModule(APIModule):
    def __init__(self):
        super(MQTTConnectorAPIModule, self).__init__()
        self.manager = MQTTConnectorManager()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_GENERATE_DEVICE_DATA: self.generate_device_data,
            ACTION_KEY_SAVE_MQTT_DEVICE: self.save_mqtt_device
        }

        return mappings

    def generate_device_data(self, user, request, db):
        data = self.manager.generate_device_data(user, request['location'], db)
        return Status(type=STATUS_OK, data=data)

    def save_mqtt_device(self, user, request, db):
        data = self.manager.save_mqtt_device(user, request['type'], request['location'], request['id'],
                                                       request['devicedata'], db)
        return Status(type=STATUS_OK, data=data)