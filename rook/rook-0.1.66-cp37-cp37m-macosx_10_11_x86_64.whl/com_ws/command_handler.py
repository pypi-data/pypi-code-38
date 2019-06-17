import json

class CommandHandler(object):
    def __init__(self, agent_com, aug_manager):
        self._agent_com = agent_com
        self._aug_manager = aug_manager

        self._agent_com.on("InitialAugsCommand", self._handle_initial_augs)
        self._agent_com.on("AddAugCommand", self._handle_add_aug)
        self._agent_com.on("RemoveAugCommand", self._handle_remove_aug)

    def _handle_initial_augs(self, initial_augs):
        self._aug_manager.clear_augs()

        for aug in initial_augs.augs:
            self._aug_manager.add_aug(json.loads(aug))

    def _handle_add_aug(self, command):
        self._aug_manager.add_aug(json.loads(command.aug_json))

    def _handle_remove_aug(self, command):
        self._aug_manager.remove_aug(command.aug_id)

    def __del__(self):
        pass
