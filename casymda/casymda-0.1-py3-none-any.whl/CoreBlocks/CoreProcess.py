from casymda.CoreBlocks.CoreComponent import CoreComponent


# processed entity waits for process time (timeout) before being forwarded to the successor

class CoreProcess(CoreComponent):
    def __init__(self, env, name, xy=None, processTime=1.0, ways={}):
        super().__init__(env, name, xy=xy, ways=ways)
        # set processTime
        self.processTime = processTime

    def actualProcessing(self, entity):
        # calc elapsed processing time (wip init)
        processTime = self.processTime - (self.env.now - entity.timeOfArrival)
        yield self.env.timeout(processTime)
