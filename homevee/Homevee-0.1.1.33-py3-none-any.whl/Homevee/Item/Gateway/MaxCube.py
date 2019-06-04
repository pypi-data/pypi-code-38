import json

from pymax.cube import Cube

from Homevee.Item.Gateway import Gateway


class MaxCube(Gateway):
    def __init__(self, gateway):
        super(MaxCube, self).__init__(gateway.name, gateway.ip,
            gateway.port, gateway.key1, gateway.key2, gateway.type)

    def get_devices(self):
        data = []
        with Cube(self.ip) as cube:
            for room in cube.rooms:
                for device in room.devices:
                    devicedata = {}
                    devicedata['room'] = room.name
                    devicedata['title'] = device.name
                    # devicedata['temp'] = device.temperature
                    devicedata['id'] = device.serial
                    data.append(devicedata)
        return json.dumps(data)