from casymda.CoreBlocks.CoreComponent import CoreComponent


# release requested resource

class CoreReleaseRes(CoreComponent):
    def __init__(self, env, name, resourceToRelease, xy=None, ways={}):
        super().__init__(env, name, xy, ways=ways)

        self.resourceToRelease = resourceToRelease

    def actualProcessing(self, entity):

        # find request of defined resource in entity requests list
        req = next(
            x for x in entity.seizedResources if x.resource is self.resourceToRelease)

        # is done immediately, but necessary for generator behavior
        yield self.resourceToRelease.release(req)
