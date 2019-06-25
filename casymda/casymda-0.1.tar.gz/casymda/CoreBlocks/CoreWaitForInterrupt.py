import simpy
from casymda.CoreBlocks.CoreComponent import CoreComponent


# processed entity waits for interrupt before being forwarded to the successor

class CoreWaitForInterrupt(CoreComponent):
    def __init__(self, env, name, xy=None, ways={}):
        super().__init__(env, name, xy=xy, ways=ways)

    # note: entity.currentProcess might be used for interrupt
    def actualProcessing(self, entity):
        try:
            yield self.env.timeout(float('inf'))
        except simpy.Interrupt:
            pass
