from Homevee.Exception import AbstractFunctionCallException
from Homevee.Item.Device import Device
from Homevee.Utils.Database import Database


class Thermostat(Device):
    def __init__(self, name, icon, location, id=None, temp=None):
        super(Thermostat, self).__init__(name, icon, location, id=id)
        self.temp = temp

    def set_temp(self, temp, db: Database = None):
        if db is None:
            db = Database()
        if(self.update_temp(temp)):
            self.mode = temp
            self.save(db)
            return True
        return False

    def update_temp(self, temp: float, db=None) -> bool:
        """
        Updates the temperatur of the thermostat
        :param temp: the new temp
        :param db: the database connection
        :return: true if successful, false otherwise
        """
        raise AbstractFunctionCallException("Thermostat.update_mode() is abstract")

    def get_min_max(self) -> tuple:
        """
        Returns a tuple with the temperature range
        :return: the minimum and maximum temperature value
        """
        raise AbstractFunctionCallException("Thermostat.get_min_max() is abstract")

    #@staticmethod
    #def get_all(location=None, db: Database = None):
    #   if db is None:
    #       db = Database()
    #    # get all devices of all types
    #    devices = []
    #    devices.extend(Switch.get_all(location))
    #    return devices