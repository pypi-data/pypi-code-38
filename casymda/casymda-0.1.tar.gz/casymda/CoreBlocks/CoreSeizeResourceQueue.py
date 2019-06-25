from casymda.CoreBlocks.CoreComponent import CoreComponent


# waiting for free resource before seizing and moving forward

class CoreSeizeResourceQueue(CoreComponent):
    def __init__(self, env, name, resourceToRequest, xy=None, ways={}):
        super().__init__(env, name, xy, ways=ways)

        self.resourceToRequest = resourceToRequest

    def actualProcessing(self, entity):

        req = self.resourceToRequest.request()
        yield req
        entity.seizedResources.append(req)
