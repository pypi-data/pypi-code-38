from trosnoth.utils.event import Event


class LifeSpan(object):
    '''
    Used by anything which may end at some point (e.g., level, trigger,
    server). Allows registration of things which should also be torn down
    when this LifeSpan ends.
    '''

    def __init__(self, parent=None, parents=None):
        self.ended = False
        self.onEnded = Event([])

        if parent:
            parent.onEnded.addListener(self.stop)
        if parents:
            for p in parents:
                p.onEnded.addListener(self.stop)

    def stop(self):
        if self.ended:
            return
        self.ended = True
        self.onEnded()

        # Prevent this lifespan being used after it's ended
        self.onEnded.clear()
        self.onEnded = None
