from Homevee.Exception import AbstractFunctionCallException
from Homevee.Item.Device import Device
from Homevee.Utils.Database import Database


class Switch(Device):
    def __init__(self, name, icon, location, id=None, mode=False):
        super(Switch, self).__init__(name, icon, location, id=id)

        if mode == 1:
            self.mode = True
        else:
            self.mode = False

    def set_mode(self, mode: bool, db: Database = None):
        if db is None:
            db = Database()
        """
        Sets the mode of the switch-device
        :param mode: the new mode
        :param db: the database connection
        :return:
        """
        #TODO sicherstellen, dass mode immer boolean ist (Ticket #26)
        if mode == "1" or mode == 1 or mode == True:
            mode = True
        else:
            mode = False

        if(self.update_mode(mode)):
            self.mode = mode
            self.save(db)

    def update_mode(self, mode: bool, db: Database = None) -> bool:
        """
        Update the mode of the switch-device
        :param mode: the mode to set the device to
        :param db: the database connection
        :return: true if the mode has been successfully updated, false otherwise
        """
        raise AbstractFunctionCallException("Switch.update_mode() is abstract")

    #@staticmethod
    #def get_all(location=None, db: Database = None):
    #    if db is None:
    #        db = Database()
    #    # get all devices of all types
    #    devices = []
    #    devices.extend(Switch.get_all(location))
    #    return devices