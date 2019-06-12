'''
This module contains the classes used by the main Bot base class in order to
follow orders like moving to an orb or attacking an enemy.
'''

import logging
from math import atan2

from trosnoth.const import ZONE_CAP_DISTANCE
from trosnoth.messages import AimPlayerAtMsg, RespawnRequestMsg, BuyUpgradeMsg
from trosnoth.model.upgrades import Bomber
from trosnoth.utils.math import distance, isNear

log = logging.getLogger(__name__)


class BotOrder(object):
    '''
    Base class for the simple bot orders.
    '''

    def __init__(self, bot):
        self.bot = bot

    def start(self):
        pass

    def restart(self):
        self.start()

    def tick(self):
        pass

    def playerDied(self):
        pass

    def playerRespawned(self):
        pass


class StandStill(BotOrder):
    '''
    This is the default order. It does not tell the bot to do anything.
    '''

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.bot == other.bot

    def playerDied(self):
        self.bot.orderFinished()

    def playerRespawned(self):
        self.bot.orderFinished()


class MoveGhostToPoint(BotOrder):
    '''
    Points the ghost towards the given point, stopping when it reaches that
    point or when it enters the given zone, whichever happens first.
    '''

    def __init__(self, bot, pos, stopOnZoneEntry=None):
        super(MoveGhostToPoint, self).__init__(bot)
        self.pos = pos
        self.stopOnZoneEntry = stopOnZoneEntry
        self.recheckIn = 0

    def start(self):
        self._doAim()

    def _doAim(self):
        playerPos = self.bot.player.pos
        dx = self.pos[0] - playerPos[0]
        dy = self.pos[1] - playerPos[1]
        theta = atan2(dx, -dy)

        self.bot.sendRequest(
            AimPlayerAtMsg(theta, 1.0, self.bot.world.lastTickId))
        self.recheckIn = 20

    def tick(self):
        self.recheckIn -= 1
        if self.bot.player.ghostThrust == 0 or self.recheckIn <= 0:
            self._doAim()

        if self.stopOnZoneEntry:
            if self.bot.player.getZone() == self.stopOnZoneEntry:
                self.bot.orderFinished()
                return
        else:
            if distance(self.bot.player.pos, self.pos) < ZONE_CAP_DISTANCE:
                self.bot.orderFinished()
                return


class PathFindingOrder(BotOrder):
    '''
    Base class for orders that need to do path finding through the map.
    '''
    RECHECK_TICKS = 20

    def __init__(self, *args, **kwargs):
        super(PathFindingOrder, self).__init__(*args, **kwargs)
        self.recheckCounter = 0
        self.forceNewRoute = True

    def start(self):
        self.recheckCounter = 0
        self.forceNewRoute = True
        if self.bot.player.bomber:
            self.bot.sendRequest(BuyUpgradeMsg(
                Bomber.upgradeType, self.bot.world.lastTickId))

    def tick(self):
        self.recheckCounter -= 1
        if self.recheckCounter <= 0 or self.forceNewRoute:
            self.checkRoute()
            self.recheckCounter = self.RECHECK_TICKS

        if not self.bot.hasUnfinishedRoute():
            self.finishedRoute()

    def checkRoute(self):
        currentRoute = self.bot.getOrCreateRoute()
        if (not self.forceNewRoute) and self.isRouteGoodEnough(currentRoute):
            return
        self.forceNewRoute = False

        currentRoute.truncateAtNextOpportunity()
        currentRoute.extendTo(self.getTargetPos())

    def finishedRoute(self):
        '''May be overridden by subclasses.'''
        self.bot.orderFinished()

    def isRouteGoodEnough(self, route):
        '''May be overridden by subclasses.'''
        return True

    def getTargetPos(self):
        '''
        Subclasses should override this to provide the position that we're
        currently aiming for.
        '''
        raise NotImplementedError(
            '{}.getTargetPos'.format(self.__class__.__name__))

    def playerDied(self):
        self.bot.orderFinished()


class Orderable(object):
    key = None

    def __eq__(self, other):
        return self.key == other.key

    def __neq__(self, other):
        return self.key != other.key

    def __gt__(self, other):
        return self.key > other.key

    def __ge__(self, other):
        return self.key >= other.key

    def __lt__(self, other):
        return self.key < other.key

    def __le__(self, other):
        return self.key <= other.key


class MoveToOrb(PathFindingOrder):
    '''
    Moves the given live player towards the given orb, stopping after touching
    the orb, or upon entering the zone if stopOnEntry is True.
    '''

    def __init__(self, bot, zone, stopOnEntry=False):
        super(MoveToOrb, self).__init__(bot)
        self.zone = zone
        self.stopOnEntry = stopOnEntry

    def __repr__(self):
        return 'MoveToOrb({bot}, {zone}{stopOnEntry})'.format(
            bot=self.bot,
            zone=self.zone,
            stopOnEntry=', stopOnEntry=True' if self.stopOnEntry else '',
        )

    def getTargetPos(self):
        return self.zone.defn.pos

    def tick(self):
        if self.stopOnEntry:
            player = self.bot.player
            playerZone = player.getZone()
            if playerZone == self.zone and player.isStationary():
                self.bot.orderFinished()
                return

        super().tick()


class RespawnInZone(BotOrder):
    '''
    If the specified zone was not respawnable when the order was given, waits
    until it is. If it was but the zone becomes unrespawnable, the order is
    considered completed.
    '''

    def __init__(self, bot, zone):
        super(RespawnInZone, self).__init__(bot)
        self.zone = zone
        self.wasRespawnable = self.bot.player.isZoneRespawnable(zone)
        self.nextCheckTime = 0

    def start(self):
        self._reAim()

    def _reAim(self):
        now = self.bot.world.getMonotonicTime()
        dist = distance(self.bot.player.pos, self.zone.defn.pos)

        if dist < 100:
            if self.bot.player.ghostThrust:
                self.bot.sendRequest(
                    AimPlayerAtMsg(0, 0, self.bot.world.lastTickId))
        elif dist < 300 or self.nextCheckTime < now:
            playerPos = self.bot.player.pos
            zonePos = self.zone.defn.pos
            dx = zonePos[0] - playerPos[0]
            dy = zonePos[1] - playerPos[1]
            theta = atan2(dx, -dy)
            thrust = min(1, distance(playerPos, zonePos) / 300.)

            self.bot.sendRequest(
                AimPlayerAtMsg(theta, thrust, self.bot.world.lastTickId))

            now = self.bot.world.getMonotonicTime()
            self.nextCheckTime = now + 0.5

    def tick(self):
        player = self.bot.player

        zoneRespawnable = self.bot.player.isZoneRespawnable(self.zone)
        if self.wasRespawnable and not zoneRespawnable:
            self.bot.orderFinished()
            return

        playerZone = player.getZone()
        if player.ghostThrust or playerZone != self.zone:
            self._reAim()

        if not player.world.abilities.respawn:
            return
        if player.timeTillRespawn > 0:
            return

        if playerZone != self.zone:
            return
        if not zoneRespawnable:
            return
        if playerZone.frozen:
            return
        self.bot.sendRequest(
            RespawnRequestMsg(self.bot.world.lastTickId))

    def playerRespawned(self):
        self.bot.orderFinished()


class FollowPlayer(PathFindingOrder):
    '''
    Follows the given target player until that player dies or this player dies.
    If attack is True, shoots at the player.
    '''

    def __init__(self, bot, player, attack=False):
        super(FollowPlayer, self).__init__(bot)
        self.targetPlayer = player
        self.attack = attack

    def finishedRoute(self):
        # May need to be recalculated
        pass

    def isRouteGoodEnough(self, route):
        if route.finishPoint is None:
            # Route isn't yet sure where it will end
            return True

        # Don't recalculate the route if we're still far from the target
        target = self.getTargetPos()
        error = distance(route.finishPoint, target)
        total = distance(self.bot.player.pos, target)
        if isNear(total, 0):
            return isNear(error, 0)
        if error / total >= 0.2:
            return False
        return True

    def getTargetPos(self):
        '''
        Subclasses should override this to provide the position that we're
        currently aiming for.
        '''
        return self.targetPlayer.pos

    def tick(self):
        if self.targetPlayer.dead:
            # We can't follow a dead player
            self.bot.orderFinished()
            return
        super().tick()


class MoveToPoint(PathFindingOrder):

    def __init__(self, bot, pos):
        super(MoveToPoint, self).__init__(bot)
        self.pos = pos

    def getTargetPos(self):
        '''
        Subclasses should override this to provide the position that we're
        currently aiming for.
        '''
        return self.pos


class CollectTrosball(PathFindingOrder):
    '''
    Moves towards the trosball until someone picks it up or this player dies.
    '''

    def finishedRoute(self):
        # Route will need to be recalculated again since we don't have the
        # Trosball yet.
        pass

    def isRouteGoodEnough(self, route):
        if route.finishPoint is None:
            # Route isn't yet sure where it will end
            return True

        # Don't recalculate the route if we're still far from the target
        target = self.getTargetPos()
        error = distance(route.finishPoint, target)
        total = distance(self.bot.player.pos, target)
        if error / total >= 0.2:
            return False
        return True

    def getTargetPos(self):
        '''
        Subclasses should override this to provide the position that we're
        currently aiming for.
        '''
        return self.bot.world.trosballManager.getPosition()

    def tick(self):
        if self.bot.world.trosballManager.trosballPlayer is not None:
            # Someone has the Trosball, so this order can't continue
            self.bot.orderFinished()
            return
        super().tick()
