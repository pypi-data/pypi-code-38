from Homevee.APIModule import APIModule
from Homevee.Item.Status import *
from Homevee.Manager.ControlManager.DimmerManager import DimmerManager

ACTION_KEY_SET_DIMMER = "setdimmer"

class DimmerAPIModule(APIModule):
    def __init__(self):
        super(DimmerAPIModule, self).__init__()
        self.dimmer_manager = DimmerManager()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_SET_DIMMER: self.set_dimmer
        }

        return mappings

    def set_dimmer(self, user, request, db):
        self.dimmer_manager.set_dimmer(user, request['type'], request['id'], request['value'], db)
        return Status(type=STATUS_OK)