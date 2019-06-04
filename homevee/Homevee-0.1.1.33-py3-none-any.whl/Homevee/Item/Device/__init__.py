from Homevee.Exception import AbstractFunctionCallException, InvalidParametersException
from Homevee.Item import Item
from Homevee.Item.Room import Room
from Homevee.Utils.Database import Database


class Device(Item):
    def __init__(self, name, icon, location, id=None):
        super(Device, self).__init__()

        self.id = id
        self.name = name
        self.icon = icon
        self.location = location

    def get_device_type(self) -> str:
        """
        Returns the devices type string
        :return: the device type
        """
        raise AbstractFunctionCallException("Device.get_device_type() is abstract")

    def get_dict(self, fields=None):
        output_dict = {}

        dict = self.build_dict()

        if (fields is None):
            output_dict = dict
        else:
            try:
                for field in fields:
                    output_dict[field] = dict[field]
            except:
                raise InvalidParametersException("InvalidParams given for get_dict()")

        output_dict['device_type'] = self.get_device_type()

        return output_dict

    @staticmethod
    def get_all(module, location=None, db: Database = None):
        if db is None:
            db = Database()
        devices = []

        if not isinstance(location, Room):
            location = Item.load_from_db(Room, location)

        #print("get all from location: "+location.name+" ("+str(location.id)+")")

        all_devices = module.load_all(db)

        if location is None or location == "all":
            # get all devices of all types
            return all_devices

        for device in all_devices:
            #print("location: "+str(device.location)+" == "+str(location.id))
            if str(device.location) == str(location.id):
                #print("append...")
                print(device.get_dict())
                devices.append(device)

        return devices