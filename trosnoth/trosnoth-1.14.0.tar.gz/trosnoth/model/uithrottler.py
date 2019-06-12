import logging

from trosnoth.const import TICK_PERIOD
from trosnoth.model.hub import Hub, Node
from trosnoth.messages import TickMsg
from trosnoth.utils.twist import WeakLoopingCall
from trosnoth.utils.utils import timeNow

log = logging.getLogger(__name__)


class UIMsgThrottler(Hub, Node):
    '''
    This class is used for RemoteGames which are connected to the UI. It delays
    messages a little bit, in order that the UI can smoothly display what is
    happening even if there is some variation in network round trip time.
    '''

    def __init__(self, *args, **kwargs):
        super(UIMsgThrottler, self).__init__(*args, **kwargs)
        self.lagAnalyser = LagAnalyser()
        self.agentEventGroups = [[]]
        self._tweenFraction = 1
        self._uiCatchUp = 0

    def stop(self):
        pass

    def disconnectNode(self):
        super(UIMsgThrottler, self).disconnectNode()
        self.hub.disconnectNode()

    def connectNewAgent(self, authTag=0):
        return self.hub.connectNewAgent(authTag=authTag)

    def disconnectAgent(self, agentId):
        if self.hub:
            self.hub.disconnectAgent(agentId)

    def sendRequestToGame(self, agentId, msg):
        if self.hub:
            self.hub.sendRequestToGame(agentId, msg)

    def gotServerCommand(self, msg):
        msg.tracePoint(self, 'gotServerCommand')
        if isinstance(msg, TickMsg):
            self.agentEventGroups[-1].append((self.node.gotServerCommand, msg))
            self.agentEventGroups.append([])

            self.lagAnalyser.gotTick()
            idealLag = self.lagAnalyser.getIdealUILag()
            tweenFraction = self._tweenFraction
            currentLag = (
                len(self.agentEventGroups) - tweenFraction) * TICK_PERIOD
            self._uiCatchUp = currentLag - idealLag
        elif msg.pumpAllEvents:
            self.agentEventGroups[-1].append((self.node.gotServerCommand, msg))
            self.pumpEvents()
        elif msg.isControl:
            self.node.gotServerCommand(msg)
        else:
            self.agentEventGroups[-1].append((self.node.gotServerCommand, msg))

    def gotMessageToAgent(self, agentId, msg):
        if msg.isControl:
            self.node.gotMessageToAgent(agentId, msg)
        else:
            self.agentEventGroups[-1].append((
                self.node.gotMessageToAgent, agentId, msg))

    def agentDisconnected(self, agentId):
        self.node.agentDisconnected(agentId)

    def releaseEventGroup(self):
        if len(self.agentEventGroups) < 2:
            self._tweenFraction = 1
            return
        group = self.agentEventGroups.pop(0)
        for event in group:
            event[-1].tracePoint(self, 'releaseEventGroup')
            event[0](*event[1:])
        self._tweenFraction = max(0, self._tweenFraction - 1)

    def uiTick(self, deltaT):
        '''
        Called to indicate that the UI has advanced by the given time delta.
        Returns the tween fraction to use in the UI.
        '''
        origDeltaT = deltaT
        catchUp = self._uiCatchUp - deltaT
        deltaT = max(0, deltaT + catchUp * (1 - 0.1 ** deltaT))

        self._uiCatchUp -= (deltaT - origDeltaT)
        self._tweenFraction += deltaT / TICK_PERIOD
        while self._tweenFraction > 1:
            # If the frame rate is really low, we may have to tick more than
            # one frame at a time.
            self.releaseEventGroup()
        return self._tweenFraction

    def pumpEvents(self):
        '''
        Causes us to immediately release all event groups.
        '''
        self.agentEventGroups.append([])
        while len(self.agentEventGroups) >= 2:
            self.releaseEventGroup()
        self._tweenFraction = 1
        self._uiCatchUp = 0


class LocalGameTweener(object):
    '''
    Used in place of a UIMsgThrottler for a local game to simply get the
    current tween fraction.
    '''
    def __init__(self, game):
        self.game = game
        self.tweenFraction = 0
        game.onServerCommand.addListener(self.gotServerCommand)

    def stop(self):
        self.game.onServerCommand.removeListener(self.gotServerCommand)

    def gotServerCommand(self, msg):
        if isinstance(msg, TickMsg):
            self.tweenFraction -= 1

    def uiTick(self, deltaT):
        self.tweenFraction += deltaT / TICK_PERIOD
        if self.tweenFraction < 0:
            self.tweenFraction = 0
        elif self.tweenFraction > 2:
            # Could be just after a pause, so a jump's ok as we catch up
            self.tweenFraction = 1
        elif self.tweenFraction >= 1:
            self.game.world.requestTickNow()
            if self.tweenFraction > 1:
                # Game is still paused / AI data is still loading
                self.tweenFraction = 1
        return self.tweenFraction


class LagAnalyser(object):
    TIME_SPAN = 5
    NOTE_TIME = 0.1

    def __init__(self):
        self.lastNote = None
        self.ignoreUntil = None
        self.reset()
        self.monitor = WeakLoopingCall(self, 'notePeriod')
        self.monitor.start(self.NOTE_TIME)

    def reset(self):
        self.startTime = timeNow()
        self.ticks = [self.startTime]

    def notePeriod(self):
        '''
        Called periodically to allow the analyser to notice if the reactor is
        not running smoothly.
        '''
        now = timeNow()
        if self.lastNote is None:
            self.lastNote = now
            return
        period = now - self.lastNote
        self.lastNote = now

        if period - self.NOTE_TIME >= self.NOTE_TIME:
            # Reactor congestion: reset tally
            self.ignoreUntil = now + self.NOTE_TIME

    def gotTick(self):
        now = timeNow()

        if self.ignoreUntil is not None:
            if now > self.ignoreUntil:
                self.reset()
            else:
                return

        self.ticks.append(now)
        limit = now - self.TIME_SPAN
        while self.ticks[0] < limit:
            self.ticks.pop(0)

    def getIdealUILag(self):
        '''
        Based on the ticks received, calculates the time which the UI should
        lag behind receiving messages, in order for things to be displayed
        smoothly.
        '''
        final = self.ticks[-1]
        initial = max(self.startTime, final - self.TIME_SPAN)

        oldT = initial
        oldValue = upper = lower = 0
        for t in self.ticks:
            value = oldValue + (t - oldT)
            upper = max(upper, value)
            value -= TICK_PERIOD
            lower = min(lower, value)
            oldT, oldValue = t, value

        return upper - lower
