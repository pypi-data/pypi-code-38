from casymda.CoreBlocks.CoreComponent import CoreComponent


# chooses a successor for all incoming entities

class CoreGateway(CoreComponent):
    def __init__(self, env, name, xy=None, ways={}):
        super().__init__(env, name, xy=xy, ways=ways)

        self.succGenerator = self.roundRobin()

    def actualProcessing(self, entity):
        yield self.env.timeout(0)

    def findNextSuccessor(self, entity):
        return next(self.succGenerator)

    def roundRobin(self):
        last = -1
        while True:
            last += 1
            last %= len(self.successors)
            yield self.successors[last]
