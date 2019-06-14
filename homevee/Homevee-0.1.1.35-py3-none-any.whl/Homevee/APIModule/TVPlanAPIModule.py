from Homevee.APIModule import APIModule
from Homevee.Item.Status import *
from Homevee.Manager.TVPlanManager import TVPlanManager

ACTION_KEY_SET_TV_CHANNELS = "settvchannels"
ACTION_KEY_GET_TV_PLAN = "gettvplan"
ACTION_KEY_GET_ALL_TV_CHANNELS = "getalltvchannels"

class TVPlanAPIModule(APIModule):
    def __init__(self):
        super(TVPlanAPIModule, self).__init__()
        self.tv_manager = TVPlanManager()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_SET_TV_CHANNELS: self.set_tv_channels,
            ACTION_KEY_GET_TV_PLAN: self.get_tv_plan,
            ACTION_KEY_GET_ALL_TV_CHANNELS: self.get_all_tv_channels
        }

        return mappings

    def set_tv_channels(self, user, request, db):
        data = self.tv_manager.set_tv_channels(user, request['channels'], db)
        return Status(type=STATUS_OK)

    def get_tv_plan(self, user, request, db):
        data = self.tv_manager.get_tv_plan(user, request['time'], db)
        return Status(type=STATUS_OK, data={'data': data})

    def get_all_tv_channels(self, user, request, db):
        data = self.tv_manager.get_all_tv_channels(user, db)
        return Status(type=STATUS_OK, data={'channels': data})