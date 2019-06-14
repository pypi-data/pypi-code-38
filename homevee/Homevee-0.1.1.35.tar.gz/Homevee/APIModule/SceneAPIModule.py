from Homevee.APIModule import APIModule
from Homevee.Item.Status import *
from Homevee.Manager.ControlManager.ActionManager import ActionManager
from Homevee.Manager.SceneManager import SceneManager

ACTION_KEY_GET_ALL_SCENES = "getallscenes"
ACTION_KEY_GET_SCENES = "getscenes"
ACTION_KEY_ADD_EDIT_SCENE = "addeditscene"
ACTION_KEY_DELETE_SCENE = "deletescene"
ACTION_KEY_RUN_SCENE = "runscene"

class SceneAPIModule(APIModule):
    def __init__(self):
        super(SceneAPIModule, self).__init__()
        self.scenes_manager = SceneManager()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_GET_ALL_SCENES: self.get_all_scenes,
            ACTION_KEY_GET_SCENES: self.get_scenes,
            ACTION_KEY_ADD_EDIT_SCENE: self.add_edit_scene,
            ACTION_KEY_DELETE_SCENE: self.delete_scene,
            ACTION_KEY_RUN_SCENE: self.run_scene
        }

        return mappings

    def get_all_scenes(self, user, request, db):
        data = self.scenes_manager.get_all_scenes(user, db)
        return Status(type=STATUS_OK, data={'scenes': data})

    def get_scenes(self, user, request, db):
        data = self.scenes_manager.get_scenes(user, request['location'], db)
        return Status(type=STATUS_OK, data={'scenes': data})

    def add_edit_scene(self, user, request, db):
        self.scenes_manager.add_edit_scene(user, request['id'], request['name'], request['location'],
                                                     request['action_data'], db)
        return Status(type=STATUS_OK)

    def delete_scene(self, user, request, db):
        self.scenes_manager.delete_scene(user, request['id'], db)
        return Status(type=STATUS_OK)

    def run_scene(self, user, request, db):
        ActionManager().run_scene(user, request['id'], db)
        return Status(type=STATUS_OK)