import logging
from math import sin, cos, atan2, sqrt

from trosnoth.utils.collision import collideTrajectory
from trosnoth.utils.math import fadeValues, distance

log = logging.getLogger(__name__)


class Unit(object):
    def __init__(self, world, *args, **kwargs):
        super(Unit, self).__init__(*args, **kwargs)
        self.world = world
        self.pos = (0, 0)
        self.oldPos = None

    def getMapBlock(self):
        return self.world.map.getMapBlockAtPoint(self.pos)

    def getZone(self):
        return self.world.map.getZoneAtPoint(self.pos)

    def reset(self):
        '''
        Called once every tick before any sprite has moved.
        '''
        self.oldPos = self.pos

    def tweenPos(self, fraction):
        if self.oldPos is None:
            return self.pos
        return (
            fadeValues(self.oldPos[0], self.pos[0], fraction),
            fadeValues(self.oldPos[1], self.pos[1], fraction),
        )


class CollectableUnit(Unit):
    '''
    Base class for units which have meaningful interactions with players.
    '''
    playerCollisionTolerance = 30

    def __init__(self, *args, **kwargs):
        super(CollectableUnit, self).__init__(*args, **kwargs)
        self.history = []
        self.hitLocalPlayer = False
        self.deathPeriod = 0

    def reset(self):
        if self.world.isServer:
            self.history.append(self.pos)
        super(CollectableUnit, self).reset()

    def beat(self):
        '''
        Called once per tick but only after this unit has been removed from the
        game for some reason.
        '''
        self.deathPeriod += 1

    def clearOldHistory(self, delay):
        delay -= self.deathPeriod
        self.history[:-delay - 1] = []

    def checkCollision(self, player, delay):
        '''
        Returns True if this unit has collided with the given player, based on
        where this unit was delay frames ago.
        '''
        delay -= self.deathPeriod
        if delay == 0:
            pos = self.pos
            if self.oldPos is None:
                oldPos = self.pos
            else:
                oldPos = self.oldPos
        else:
            if delay >= len(self.history) or delay < 0:
                return False
            pos = self.history[-delay]
            oldPos = self.history[-delay - 1]

        # Check both player colliding with us and us colliding with player
        if collideTrajectory(
                player.pos, oldPos, (pos[0] - oldPos[0], pos[1] - oldPos[1]),
                self.playerCollisionTolerance):
            return True

        deltaX = player.pos[0] - player.oldPos[0]
        deltaY = player.pos[1] - player.oldPos[1]
        if collideTrajectory(
                pos, player.oldPos, (deltaX, deltaY),
                self.playerCollisionTolerance):
            return True
        return False

    def collidedWithPlayer(self, player):
        '''
        Called when this unit has collided with the given player. Note that
        this is only calculated on the server, so anything done here will not
        automatically happen on clients too. Therefore, it's a good idea to
        just send a message, and let the message handler do the hard work here.
        '''
        raise NotImplementedError(
            '%s.collidedWithPlayer' % (self.__class__.__name__,))

    def collidedWithLocalPlayer(self, player):
        '''
        Called when this unit has collided with the given local player.
        '''
        self.hitLocalPlayer = True


class Bouncy(Unit):
    stopToleranceDistance = 1
    stopToleranceTicks = 5
    dampingFactor = 0.9
    ignoreLedges = True

    def __init__(self, world, *args, **kwargs):
        super(Bouncy, self).__init__(world, *args, **kwargs)
        self.stopped = False
        self.stationaryTicks = 0

    def advance(self):
        if self.stopped:
            return

        deltaT = self.world.tickPeriod

        try:
            delta = (self.xVel * deltaT, self.yVel * deltaT)

            oldPos = self.pos
            self.pos, collision = self.world.physics.getMotion(
                self, delta, ignoreLedges=self.ignoreLedges)
            if distance(self.pos, oldPos) < self.stopToleranceDistance:
                self.stationaryTicks += 1
                if self.stationaryTicks > self.stopToleranceTicks:
                    self.stopped = True
                    self.xVel = self.yVel = 0
                    return
            else:
                self.stationaryTicks = 0

            if collision:
                self.performRebound(collision)

            vFinal = self.yVel + self.getGravity() * deltaT
            if vFinal > self.getMaxFallVel():
                self.yVel = self.getMaxFallVel()
            else:
                self.yVel = vFinal

        except Exception:
            log.exception('Error advancing bouncy unit')

    def getGravity(self):
        raise NotImplementedError()

    def getMaxFallVel(self):
        raise NotImplementedError()

    def performRebound(self, collision):
        obsAngle = collision.angle
        shotAngle = atan2(self.yVel, self.xVel)
        dif = shotAngle - obsAngle
        final = obsAngle - dif
        speed = sqrt(self.xVel ** 2 + self.yVel ** 2) * self.dampingFactor
        self.xVel = speed * cos(final)
        self.yVel = speed * sin(final)


class PredictedTrajectory(object):
    def predictedTrajectoryPoints(self):
        raise NotImplementedError('{}.predictedTrajectoryPoints'.format(
            self.__class__.__name__))

    def explosionRadius(self):
        return 0


class PredictedBouncyTrajectory(PredictedTrajectory, Bouncy):
    '''
    The trajectory of a grenade, without the explodey bits
    '''
    def __init__(
            self, world, player, duration, initialVelocity, gravity,
            maxFallVelocity, *args, **kwargs):
        Bouncy.__init__(self, world, *args, **kwargs)
        self.duration = duration
        self.player = player
        self.gravity = gravity
        self.maxFallVel = maxFallVelocity
        self.initialVelocity = initialVelocity

    def getGravity(self):
        return self.gravity

    def getMaxFallVel(self):
        return self.maxFallVel

    def predictedTrajectoryPoints(self):
        self.stopped = False
        self.timeLeft = self.duration
        self.pos = self.oldPos = self.player.pos
        angle = self.player.angleFacing
        self.xVel = self.initialVelocity * sin(angle)
        self.yVel = -self.initialVelocity * cos(angle)
        while self.timeLeft > 0 and not self.stopped:
            yield self.pos
            self.advance()
            self.timeLeft -= self.world.tickPeriod
