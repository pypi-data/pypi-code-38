from casymda.CoreBlocks.CoreComponent import CoreComponent
from casymda.CoreBlocks.CoreEntity import CoreEntity


# the source has a scheduled "creationloop" process, which creates entities and then processes them regularly
# (as if the entity just entered a normal core-component, but with 0 time delay)

class CoreSource(CoreComponent):
    def __init__(self, env, name, xy=None, ways={}, entityType=CoreEntity, interArrivalTime=0, maxEntities=5):

        super().__init__(env, name, xy, ways=ways)

        self.entityType = entityType
        self.interArrivalTime = interArrivalTime
        self.maxEntities = maxEntities

        self.entityCounter = 0

        self.env.process(self.creationLoop())

    def creationLoop(self):
        # this additional call is added due to WIP init (enables reduction of maxEntities before starting)
        yield self.env.timeout(self.interArrivalTime)
        for _ in range(self.maxEntities):
            self.entityCounter += 1
            entity = self.entityType(
                self.env, "entity_" + str(self.entityCounter))

            entity.component_resource_request = self.component_resource.request()
            yield entity.component_resource_request

            self.env.process(self.processEntity(entity))
            yield self.env.timeout(self.interArrivalTime)

    def actualProcessing(self, entity):
        yield self.env.timeout(0)
