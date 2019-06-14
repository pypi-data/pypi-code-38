from Homevee.APIModule import APIModule
from Homevee.Item.Status import *
from Homevee.Updater import Updater

ACTION_KEY_CHECK_FOR_UPDATES = "checkforupdates"
ACTION_KEY_UPDATE_SYSTEM = "updatesystem"

class UpdaterAPIModule(APIModule):
    def __init__(self):
        super(UpdaterAPIModule, self).__init__()
        self.update_manager = Updater()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_CHECK_FOR_UPDATES: self.check_for_updates,
            ACTION_KEY_UPDATE_SYSTEM: self.update_system
        }

        return mappings

    def check_for_updates(self, user, request, db):
        data = self.update_manager.check_for_updates()
        return Status(type=STATUS_OK, data=data)

    def update_system(self, user, request, db):
        self.update_manager.do_homevee_update(user, db)
        return Status(type=STATUS_OK)