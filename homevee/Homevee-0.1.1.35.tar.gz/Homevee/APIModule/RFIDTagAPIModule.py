from Homevee.APIModule import APIModule
from Homevee.Item.Status import *
from Homevee.Manager.ControlManager.RFIDTagManager import RFIDTagManager

ACTION_KEY_GET_RFID_TAGS = "getrfidtags"
ACTION_KEY_ADD_EDIT_RFID_TAG = "addeditrfidtag"
ACTION_KEY_DELETE_RFID_TAG = "deleterfidtag"
ACTION_KEY_RUN_RFID_ACTION = "runrfidaction"

class RFIDTagAPIModule(APIModule):
    def __init__(self):
        super(RFIDTagAPIModule, self).__init__()
        self.rfid_tag_manager = RFIDTagManager()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_GET_RFID_TAGS: self.get_rfid_tags,
            ACTION_KEY_ADD_EDIT_RFID_TAG: self.add_edit_rfid_tag,
            ACTION_KEY_DELETE_RFID_TAG: self.delete_rfid_tag,
            ACTION_KEY_RUN_RFID_ACTION: self.run_frid_action
        }

        return mappings

    def get_rfid_tags(self, user, request, db):
        data = self.rfid_tag_manager.get_rfid_tags(user, db)
        return Status(type=STATUS_OK, data={'tags': data})

    def add_edit_rfid_tag(self, user, request, db):
        data = self.rfid_tag_manager.add_edit_rfid_tag(user, request['name'], request['uuid'], request['type'],
                                                          request['id'], db)
        return Status(type=STATUS_OK, data=data)

    def delete_rfid_tag(self, user, request, db):
        data = self.rfid_tag_manager.delete_rfid_tag(user, request['uuid'], db)
        return Status(type=STATUS_OK, data=data)

    def run_frid_action(self, user, request, db):
        data = self.rfid_tag_manager.run_rfid_action(user, request['uuid'], db)
        return Status(type=STATUS_OK, data=data)