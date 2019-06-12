import logging
import random
from twisted.internet import reactor

from trosnoth.bots.base import Bot
from trosnoth.messages import TickMsg
from trosnoth.utils.event import Event

log = logging.getLogger(__name__)


class GoalSetterBot(Bot):
    '''
    Base class for bots which mainly operate by setting high-level goals, which
    may themselves set subgoals.
    '''

    # Override this in subclasses to set the main goal for this bot to achieve
    MainGoalClass = None

    def start(self):
        super(GoalSetterBot, self).start()

        self.onTick = Event()
        self.onOrderFinished = Event()
        self.recentGoals = {}
        self.clearRecent = None
        self.mainGoal = self.MainGoalClass(self, None)

        self.mainGoal.start()

    def disable(self):
        super(GoalSetterBot, self).disable()
        self.mainGoal.stop()
        if self.clearRecent:
            self.clearRecent.cancel()
            self.clearRecent = None

    def showGoalStack(self):
        '''
        For debugging.
        '''
        log.error('Goal stack for %s:', self.player)
        curGoal = self.mainGoal
        while curGoal:
            log.error('  %s', curGoal)
            curGoal = curGoal.subGoal
        log.error('')

    def subGoalStopped(self, goal):
        # Record recent inactive goals so they can be reused if they come up
        # again.
        self.recentGoals[goal] = goal
        if self.clearRecent:
            self.clearRecent.cancel()
            self.clearRecent = None
        self.clearRecent = self.world.callLater(4, self.clearRecentGoals)

    def startingSubGoal(self, goal):
        if goal in self.recentGoals:
            del self.recentGoals[goal]

    def clearRecentGoals(self):
        self.clearRecent = None
        self.recentGoals.clear()

    def checkGoal(self, goal):
        result = self.recentGoals.get(goal, goal)
        result.parent = goal.parent
        return result

    @TickMsg.handler
    def handle_TickMsg(self, msg):
        self.onTick()
        super(GoalSetterBot, self).handle_TickMsg(msg)

    def orderFinished(self):
        super(GoalSetterBot, self).orderFinished()
        self.onOrderFinished()


class Goal(object):
    '''
    Represents something that the bot is trying to achieve.
    '''

    def __init__(self, bot, parent):
        self.bot = bot
        self.parent = parent
        self.subGoal = None

    def __str__(self):
        return self.__class__.__name__

    def start(self):
        '''
        Called when this goal should begin its work.
        '''
        self.reevaluate()

    def stop(self):
        '''
        Should disable any active components of this goal.
        '''
        if self.subGoal:
            self.subGoal.stop()
            self.subGoal.parent = None
            self.bot.subGoalStopped(self.subGoal)
            self.subGoal = None

    def setSubGoal(self, goal):
        '''
        If the given goal is already the current sub-goal, does nothing.
        Otherwise, stops the current sub-goal, and starts the given one.
        '''
        if self.subGoal == goal:
            return
        if self.subGoal:
            self.subGoal.stop()
            self.subGoal.parent = None
            self.bot.subGoalStopped(goal)

        if goal:
            goal = self.bot.checkGoal(goal)
            self.subGoal = goal
            self.bot.startingSubGoal(goal)
            goal.start()
        else:
            self.subGoal = None

    def returnToParent(self):
        '''
        Call this method to tell the parent goal that this goal is either
        completed, or no longer relevant.
        '''
        if self.parent:
            reactor.callLater(0, self.parent.returnedFromChild, self)

    def returnedFromChild(self, child):
        '''
        Called by child's returnToParent() method. The default implementation
        checks that the returning child is this goal's subgoal, then calls
        reevaluate().
        '''
        if child is self.subGoal:
            self.reevaluate()
        else:
            child.stop()
            child.parent = None
            self.bot.subGoalStopped(child)

    def reevaluate(self):
        '''
        Called by the default implementations of start() and
        returnedFromChild() to determine what this goal should do next.
        '''
        pass


class ZoneMixin(Goal):
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return other.zone == self.zone

    def __hash__(self):
        return hash(self.zone)

    def __str__(self):
        return '%s(%s)' % (self.__class__.__name__, self.zone)


class MessAroundInZone(Goal):
    '''
    Wander around in the zone the player is in at the time of construction.
    Aborts if the player dies or leaves the zone.
    '''

    def __init__(self, bot, parent):
        super(MessAroundInZone, self).__init__(bot, parent)
        self.zone = self.bot.player.getZone()

    def start(self):
        if self.bot.player.dead:
            raise RuntimeError('dead bots cannot mess around')

        self.bot.onTick.addListener(self.tick)
        self.bot.standStill()
        super(MessAroundInZone, self).start()

    def stop(self):
        super(MessAroundInZone, self).stop()
        self.bot.onTick.removeListener(self.tick)

    def reevaluate(self):
        if self.bot.player.dead:
            self.returnToParent()
            return

        if self.bot.hasUnfinishedRoute():
            return

        zone = self.bot.player.getZone()
        if zone != self.zone:
            self.returnToParent()
            return

        pathFinder = self.bot.world.map.layout.pathFinder
        routes = pathFinder.getPossibleActions(self.bot.player)
        if not routes:
            self.returnToParent()
            return

        # Limit to actions that stay in the same zone
        okRoutes = [
            r for r in routes
            if r.finishPoint is None or self.bot.world.map.getZoneAtPoint(
                r.finishPoint) == self.zone]
        if okRoutes:
            routes = okRoutes

        # Make sure there's no other order that might be competing
        self.bot.standStill()
        self.bot.setRoute(random.choice(routes))

    def tick(self):
        player = self.bot.player
        if player.dead:
            self.returnToParent()
            return

        if not self.bot.hasUnfinishedRoute():
            self.reevaluate()


class RespawnNearPlayer(Goal):
    def __init__(self, bot, parent, target):
        super(RespawnNearPlayer, self).__init__(bot, parent)
        self.target = target

    def start(self):
        self.nextCheck = None
        super(RespawnNearPlayer, self).start()

    def stop(self):
        if self.nextCheck:
            self.nextCheck.cancel()
        super(RespawnNearPlayer, self).stop()

    def reevaluate(self):
        player = self.bot.player
        world = self.bot.world
        if not player.dead or self.target not in world.players:
            self.returnToParent()
            return

        if self.nextCheck:
            self.nextCheck.cancel()
        delay = 1 + random.random()
        self.nextCheck = world.callLater(delay, self.reevaluate)

        zone = self.target.getZone()
        if zone is not None:
            self.setSubGoal(RespawnNearZone(self.bot, self, zone))


class RespawnNearZone(ZoneMixin, Goal):
    '''
    Respawns in a zone that's as close as possible to the given zone.
    '''

    def __init__(self, bot, parent, zone):
        super(RespawnNearZone, self).__init__(bot, parent)
        self.zone = zone
        self.nextCheck = None

    def start(self):
        self.nextCheck = None
        self.bot.world.onZoneTagged.addListener(self.zoneTagged)
        self.bot.onOrderFinished.addListener(self.orderFinished)
        super(RespawnNearZone, self).start()

    def stop(self):
        super(RespawnNearZone, self).stop()
        self.bot.world.onZoneTagged.removeListener(self.zoneTagged)
        self.bot.onOrderFinished.removeListener(self.orderFinished)
        if self.nextCheck:
            self.nextCheck.cancel()

    def zoneTagged(self, *args, **kwargs):
        '''
        We may be waiting to respawn in a zone that's just changed ownership.
        '''
        self.reevaluate()

    def orderFinished(self):
        self.reevaluate()

    def reevaluate(self):
        player = self.bot.player
        if not player.dead:
            self.returnToParent()
            return
        if self.nextCheck:
            self.nextCheck.cancel()

        bestZone = None
        zones = [self.zone]
        seen = set()

        while zones:
            zone = zones.pop(0)
            seen.add(zone)
            if player.isZoneRespawnable(zone):
                bestZone = zone
                break
            adjacent = [
                z for z in zone.getUnblockedNeighbours() if z not in seen]
            random.shuffle(adjacent)
            zones.extend(adjacent)

        if bestZone is None:
            self.bot.standStill()
            delay = 1 + random.random()
            self.nextCheck = self.bot.world.callLater(delay, self.reevaluate)
        else:
            self.bot.respawn(zone=bestZone)

