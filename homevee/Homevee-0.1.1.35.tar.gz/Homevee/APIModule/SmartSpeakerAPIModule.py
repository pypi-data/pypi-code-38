from Homevee.APIModule import APIModule
from Homevee.Item.Status import *
from Homevee.Manager.SmartSpeakerManager import SmartSpeakerManager

ACTION_KEY_GET_SMART_SPEAKERS = "getsmartspeakers"

class SmartSpeakerAPIModule(APIModule):
    def __init__(self):
        super(SmartSpeakerAPIModule, self).__init__()
        self.manager = SmartSpeakerManager()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_GET_SMART_SPEAKERS: self.get_smart_speakers
        }

        return mappings

    def get_smart_speakers(self, user, request, db):
        data = self.manager.get_smart_speakers(user, db)
        return Status(type=STATUS_OK, data={'speakers':data})