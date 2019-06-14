from Homevee.Item.Device import Device


class RGBLight(Device):
    def __init__(self, name, icon, location, id=None, mode=False):
        super(RGBLight, self).__init__(name, icon, location, id=id)