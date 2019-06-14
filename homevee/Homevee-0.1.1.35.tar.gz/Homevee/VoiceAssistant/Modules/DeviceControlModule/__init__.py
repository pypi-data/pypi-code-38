from Homevee.Utils.Database import Database
from Homevee.Utils.DeviceTypes import *
from Homevee.VoiceAssistant.Modules import VoiceModule


class VoiceDeviceControlModule(VoiceModule):

    def __init__(self, priority):
        super(VoiceDeviceControlModule, self).__init__(priority)
        self.devices_map = self.setup_devices_map()

    def find_room(self, text, db: Database = None):
        if db is None:
            db = Database()
        results = db.select_all("SELECT * FROM ROOMS", {})

        for room in results:
            position = text.find(room['NAME'].lower())
            if position is not -1:
                return room
        return None

    def setup_devices_map(self):
        devices_map = {
            WAKE_ON_LAN: ['WAKE_ON_LAN','NAME','DEVICE', WAKE_ON_LAN,'LOCATION'],
            XBOX_ONE_WOL: ['XBOX_ONE_WOL','NAME','ID', XBOX_ONE_WOL,'LOCATION'],
            FUNKSTECKDOSE: ['FUNKSTECKDOSEN', 'NAME', 'DEVICE', FUNKSTECKDOSE, 'ROOM'],
            ZWAVE_SWITCH: ['ZWAVE_SWITCHES', 'NAME', 'ID', ZWAVE_SWITCH, 'LOCATION'],
            URL_SWITCH: ['URL_SWITCH_BINARY', 'NAME', 'ID', URL_SWITCH, 'LOCATION'],
            URL_TOGGLE: ['URL_TOGGLE', 'NAME', 'ID', URL_TOGGLE, 'LOCATION'],
            PHILIPS_HUE_LIGHT: ['PHILIPS_HUE_LIGHTS', 'NAME', 'ID', PHILIPS_HUE_LIGHT, 'LOCATION'],
            URL_RGB_LIGHT: ['URL_RGB_LIGHT', 'NAME', 'ID', URL_RGB_LIGHT, 'LOCATION']
        }

        return devices_map

    def find_devices(self, text, device_types, location_key, db: Database = None):
        if db is None:
            db = Database()
        devices = []

        words = text.split()

        for device_type in device_types:
            item = self.devices_map[device_type]

            if location_key is None:
                results = db.select_all("SELECT * FROM " + item[0], {})
            else:
                param_array = {'location': location_key}
                results = db.select_all("SELECT * FROM " + item[0] + " WHERE " + item[4] + " = :location", param_array)

            for device in results:
                for word in words:
                    if word == device[item[1]].lower():
                        device_item = {'type': item[3], 'name': device[item[1]], 'id': device[item[2]]}
                        devices.append(device_item)

        '''for item in data:
            if location_key is None:
                cur.execute("SELECT * FROM "+item[0])
            else:
                param_array = {'location': location_key}
                cur.execute("SELECT * FROM "+item[0]+" WHERE "+item[4]+" = :location", param_array)

            for device in cur.fetchall():
                position = text.find(device[item[1]].lower())
                if position is not -1:
                    device_item = {'type': item[3], 'name': device[item[1]], 'id': device[item[2]]}
                    devices.append(device_item)'''

        return devices