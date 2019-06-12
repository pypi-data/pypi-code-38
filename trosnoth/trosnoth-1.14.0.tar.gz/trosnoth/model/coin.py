import logging

from trosnoth.const import DEFAULT_COIN_VALUE
from trosnoth.messages import AwardPlayerCoinMsg, RemoveCollectableCoinMsg
from trosnoth.model.physics import CollisionCircle
from trosnoth.model.unit import Bouncy, CollectableUnit
from trosnoth.utils.event import Event
from trosnoth.utils.math import distance

log = logging.getLogger(__name__)


class BouncyPlayerAttractor(Bouncy):
    '''
    Provides bounce and gravity functionality, mixed with accelerating
    towards nearby live players.
    '''
    gravity = 1000
    playerAttraction = 500
    attractiveRadius = 85

    def advance(self):
        try:
            onlyGrav, xAcc, yAcc = self.getAcceleration()
            if self.stopped and onlyGrav:
                return
            self.stopped = False

            deltaT = self.world.tickPeriod
            self.xVel += xAcc * deltaT
            self.yVel += yAcc * deltaT

            delta = (self.xVel * deltaT, self.yVel * deltaT)

            oldX, oldY = self.pos
            self.pos, collision = self.world.physics.getMotion(self, delta)
            if distance(self.pos, (oldX, oldY)) < self.stopToleranceDistance:
                self.stationaryTicks += 1
                if self.stationaryTicks > self.stopToleranceTicks:
                    self.xVel = self.yVel = 0
                    self.stopped = True
                    return
            else:
                self.stationaryTicks = 0

            if collision :
                self.performRebound(collision)

        except Exception:
            log.exception('Error advancing {}'.format(self.__class__.__name__))

    def getAcceleration(self):
        minDist = None
        closest = None
        livePlayers = [p for p in self.world.players if not p.dead]
        if livePlayers:
            minDist, discard, player = min(
                (distance(p.pos, self.pos), p.id, p) for p in livePlayers)
            if 0 < minDist < self.attractiveRadius:
                xr = (player.pos[0] - self.pos[0]) / minDist
                yr = (player.pos[1] - self.pos[1]) / minDist
                x = self.playerAttraction * xr
                if yr > 0:
                    y = self.gravity * yr
                else:
                    y = self.playerAttraction * yr
                return False, x, y
        return True, 0, self.gravity


class CollectableCoin(BouncyPlayerAttractor, CollectableUnit):
    # The following values control coin movement.
    maxFallVel = 540            # pix/s
    gravity = 1000              # pix/s/s
    dampingFactor = 0.7

    RADIUS = 5
    collisionShape = CollisionCircle(RADIUS)

    def __init__(
            self, world, id, pos, xVel, yVel, value=None, *args, **kwargs):
        super(CollectableCoin, self).__init__(world, *args, **kwargs)

        self.onVanish = Event(['coin'])

        self.id = id
        self.creationTick = self.world.getMonotonicTick()
        self.vanished = False
        self.value = value or DEFAULT_COIN_VALUE

        # Place myself.
        self.pos = pos
        self.xVel = xVel
        self.yVel = yVel

    def collidedWithPlayer(self, player):
        self.world.sendServerCommand(
            AwardPlayerCoinMsg(player.id, self.value, sound=True))

        if self.vanished:
            # It's already been removed from the main set of coins.
            self.world.deadCoins.remove(self)
        else:
            del self.world.collectableCoins[self.id]
            self.world.sendServerCommand(RemoveCollectableCoinMsg(self.id))
        self.world.onCollectableCoinRemoved(self.id)

    def removeDueToTime(self):
        self.vanished = True
        self.onVanish(self)

        self.world.deadCoins.add(self)
        del self.world.collectableCoins[self.id]
        self.world.sendServerCommand(RemoveCollectableCoinMsg(self.id))

    def getGravity(self):
        return self.gravity

    def getMaxFallVel(self):
        return self.maxFallVel
