from casymda.CoreBlocks.CoreComponent import CoreComponent


# sink; yields 0 timeout event before no further processing is started

class CoreSink(CoreComponent):
    def __init__(self, env, name, xy=None, ways={}):
        super().__init__(env, name, xy=xy)

    def processEntity(self, entity):
        yield self.env.timeout(0)

        self.onEnter(entity)
        self.entities.append(entity)
        # TODO: remove release since not required with infinite capacity
        self.component_resource.release(entity.component_resource_request)
        self.onExit(entity, None)
