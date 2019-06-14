from Homevee.Item import Item


class Scene(Item):
    def __init__(self):
        super(Scene, self).__init__()

    def run(self):
        """
        Runs the scene
        :return:
        """
        raise NotImplementedError("Scene.run() is not implemented yet")