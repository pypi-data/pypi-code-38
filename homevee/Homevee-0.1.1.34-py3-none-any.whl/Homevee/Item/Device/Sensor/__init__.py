from Homevee.Item.Device import Device

SENSOR_TYPE_MAP = {
    'temp': {'name': 'Temperatur', 'einheit': '°C', 'einheit_word': 'Grad'},
    'hygro': {'name': 'Luftfeuchtigkeit', 'einheit': '%', 'einheit_word': '%'},
    'helligkeit': {'name': 'Helligkeit', 'einheit': 'Lux', 'einheit_word': 'Lumen'},
    'uv': {'name': 'UV-Licht', 'einheit': 'UV-Index', 'einheit_word': 'UV-Index'},
    'powermeter': {'name': 'Stromverbrauch', 'einheit': 'Watt', 'einheit_word': 'Watt'},
}

class Sensor(Device):
    def __init__(self, name, icon, location, save_data, sensor_type, id=None, value=None):
        super(Sensor, self).__init__(name, icon, location, id=id)
        self.save_data = save_data
        self.sensor_type = sensor_type

        if value is None:
            value = "N/A"
        else:
            self.value = value

    def get_einheit(self) -> str:
        """
        Returns the unit for the sensor type
        :return: the unit
        """
        return SENSOR_TYPE_MAP[self.sensor_type]['einheit']