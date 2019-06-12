from trosnoth.const import TICK_PERIOD


class Trigger(object):
    '''
    Base class for defining standard triggers that multiple different levels
    might want to use.
    '''

    def __init__(self, level):
        assert level and level.world
        self.level = level
        self.world = level.world
        self.active = False

    def activate(self):
        if self.active:
            return
        self.active = True
        self.level.activeTriggers.add(self)
        self.doActivate()
        return self

    def deactivate(self):
        if not self.active:
            return
        self.active = False
        self.level.activeTriggers.discard(self)
        self.doDeactivate()

    def doActivate(self):
        '''
        Subclasses should override this to perform activation logic.
        '''
        raise NotImplementedError(
            '{}.doActivate'.format(self.__class__.__name__))

    def doDeactivate(self):
        '''
        Subclasses should override this to perform deactivation logic.
        '''
        raise NotImplementedError(
            '{}.doDeactivate'.format(self.__class__.__name__))


class DurationScoreTrigger(Trigger):
    '''
    Base class for triggers which increment player scores over time based on
    some condition.
    '''

    def __init__(self, level, interval=1):
        super(DurationScoreTrigger, self).__init__(level)
        self.interval = interval
        self.callback = None
        self.extraTicks = 0
        self.playerPortions = {}

    def doActivate(self):
        self.callback = self.world.callLater(self.interval, self.gotInterval)
        self.world.onServerTickComplete.addListener(self.gotTickComplete)

    def doDeactivate(self):
        self.world.onServerTickComplete.removeListener(self.gotTickComplete)
        if self.callback:
            self.callback.cancel()

    def gotInterval(self):
        self.callback = self.world.callLater(self.interval, self.gotInterval)
        for p in self.world.players:
            if p in self.playerPortions:
                self.world.scoreboard.playerScored(p, self.playerPortions[p])
            elif self.checkCondition(p):
                self.world.scoreboard.playerScored(p, 1)
        self.extraTicks = 0
        self.playerPortions = {}

    def gotTickComplete(self):
        self.extraTicks += 1

    def conditionLost(self, player):
        '''
        Should be called by subclasses when the given player previously met
        the condition, but no longer does.
        '''
        value = self.extraTicks * TICK_PERIOD / self.interval
        self.playerPortions.setdefault(player, value)

    def checkCondition(self, player):
        '''
        Must return whether or not the condition is true for this player.
        '''
        raise NotImplementedError('{}.checkCondition'.format(
            self.__class__.__name__))
