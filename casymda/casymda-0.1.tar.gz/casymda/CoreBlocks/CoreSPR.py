from casymda.CoreBlocks.CoreComponent import CoreComponent
from casymda.CoreBlocks.CoreResource import CoreResource

# TODO: WIP
# TODO: WIP -> order of initialized entities should be according to timeOfArrival to seize resources accodingly
# TODO: real combination of imported blocks
# ("hierarchy"-feature -> WIP snap needs to still access single components? -> that way the standard way of just comparing arrival time can be maintained)


# entities in this block follow the process: request resource, process, release

class CoreSPR(CoreComponent):
    def __init__(self, env, name, xy=None, ways={}, processTime=1.0, numResources=1):
        super().__init__(env, name, xy=xy, ways=ways)

        self.processTime = processTime

        self.resource = CoreResource(
            self.env, 'resource', capacity=numResources)

    def actualProcessing(self, entity):
        # wait for resource
        req = self.resource.request()
        yield req
        entity.seizedResources.append(req)

        if not hasattr(entity, "SPR_processingStartedAt"):
            # dictionary to save start times of processing in corresponding SPR blocks
            entity.SPR_processingStartedAt = {}

        if self.name in entity.SPR_processingStartedAt:
            processTime = self.processTime - \
                (self.env.now - entity.SPR_processingStartedAt[self.name])
        else:
            entity.SPR_processingStartedAt[self.name] = self.env.now
            processTime = self.processTime

        # do the processing
        yield self.env.timeout(processTime)

        # release resource
        req = next(
            x for x in entity.seizedResources if x.resource is self.resource)
        self.resource.release(req)
