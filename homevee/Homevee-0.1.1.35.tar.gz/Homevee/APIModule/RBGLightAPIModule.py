from Homevee.APIModule import APIModule
from Homevee.Item.Status import *
from Homevee.Manager.ControlManager.RGBLightManager import RGBLightManager

ACTION_KEY_SET_RGB = "setrgb"

class RGBLightAPIModule(APIModule):
    def __init__(self):
        super(RGBLightAPIModule, self).__init__()
        self.rgb_manager = RGBLightManager()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_SET_RGB: self.set_rgb
        }

        return mappings

    def set_rgb(self, user, request, db):
        self.rgb_manager.rgb_control(user, request['type'], request['id'], request['mode'],
                                                     request['brightness'],
                                                     request['color'], db)
        return Status(type=STATUS_OK)