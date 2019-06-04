from Homevee.Item import Item
from Homevee.Item.Logic.Action import Action
from Homevee.Item.Scene import Scene


class RunSceneAction(Action):
    def __init__(self, id):
        super(RunSceneAction, self).__init__()
        self.id = id
        self.scene = Item.load_from_db(Scene, self.id)

    def run(self):
        self.scene.run()

    @staticmethod
    def get_from_dict(dict):
        try:
            id = dict['id']
            return RunSceneAction(id)
        except:
            return None