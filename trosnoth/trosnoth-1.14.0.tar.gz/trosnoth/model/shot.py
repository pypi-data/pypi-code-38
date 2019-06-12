import copy
import logging
from math import sin, cos, atan2, sqrt

import pygame

from trosnoth.model.physics import CollisionCircle
from trosnoth.model.unit import (
    Unit, Bouncy, PredictedBouncyTrajectory, PredictedTrajectory,
)
from trosnoth.trosnothgui.ingame.utils import mapPosToScreen
from trosnoth.utils.collision import collideTrajectory
from trosnoth.utils.event import Event

log = logging.getLogger(__name__)

GRENADE_BLAST_RADIUS = 448


class LocalSprite(object):
    '''
    Mixin for representing the local player's shots and grenades.
    These go slowly until their real counterpart catches up.
    '''

    def __init__(self, *args, **kwargs):
        super(LocalSprite, self).__init__(*args, **kwargs)
        self.nextPos = None
        self.localTicks = 0
        self.realTicks = 0
        self.realShotStarted = False
        self.realShotCaughtUp = False
        self.onRealShotCaughtUp = Event(['sprite'])

    def advance(self):
        if self.realShotCaughtUp:
            super(LocalSprite, self).advance()
            return

        if self.realShotStarted:
            self.realTicks += 1

        if self.nextPos:
            self.pos = self.nextPos
            self.nextPos = None
            self.localTicks += 1
            if self.realTicks >= self.localTicks:
                self.realShotCaughtUp = True
                self.onRealShotCaughtUp(self)
        else:
            super(LocalSprite, self).advance()
            self.nextPos = self.pos
            self.pos = (
                0.5 * self.pos[0] + 0.5 * self.oldPos[0],
                0.5 * self.pos[1] + 0.5 * self.oldPos[1],
            )


class GrenadeShot(Bouncy):
    '''
    This will make the grenade have the same physics as a player without
    control and features of player movement
    '''

    RADIUS = 5
    collisionShape = CollisionCircle(RADIUS)

    def __init__(self, world, player, duration, *args, **kwargs):
        Bouncy.__init__(self, world, *args, **kwargs)
        self.player = player
        self.timeLeft = duration

        # Place myself.
        self.pos = self.oldPos = player.pos
        angle = player.angleFacing
        self.xVel = self.world.physics.grenadeInitVel * sin(angle)
        self.yVel = -self.world.physics.grenadeInitVel * cos(angle)

    def getGravity(self):
        return self.world.physics.grenadeGravity

    def getMaxFallVel(self):
        return self.world.physics.grenadeMaxFallVel

    def advance(self):
        super(GrenadeShot, self).advance()
        self.timeLeft -= self.world.tickPeriod
        if self.timeLeft <= 0:
            self.removeGrenade()
            self.propagateExplosionEvent()

    def propagateExplosionEvent(self):
        self.world.grenadeExploded(self.player, self.pos, GRENADE_BLAST_RADIUS)

    def removeGrenade(self):
        self.world.removeGrenade(self)


class LocalGrenade(LocalSprite, GrenadeShot):
    def __init__(self, localState, *args, **kwargs):
        super(LocalGrenade, self).__init__(*args, **kwargs)
        self.localState = localState

    def propagateExplosionEvent(self):
        pass

    def removeGrenade(self):
        self.localState.grenadeRemoved()


class PredictedGrenadeTrajectory(PredictedBouncyTrajectory):

    collisionShape = GrenadeShot.collisionShape

    def __init__(self, world, player, duration):
        PredictedBouncyTrajectory.__init__(self,
                                           world,
                                           player,
                                           duration,
                                           world.physics.grenadeInitVel,
                                           world.physics.grenadeGravity,
                                           world.physics.grenadeMaxFallVel)

    def explosionRadius(self):
        return GRENADE_BLAST_RADIUS


class Shot(Unit):

    NORMAL = 'normal'
    RICOCHET = 'ricochet'

    RADIUS = 3
    collisionShape = CollisionCircle(RADIUS)

    playerCollisionTolerance = 20

    def __init__(
            self, world, id, team, player, pos, velocity, kind, lifetime,
            *args, **kwargs):
        super(Shot, self).__init__(world, *args, **kwargs)

        self.onRebound = Event(['pos'])
        self.onExpire = Event([])
        self.id = id
        self.team = team
        self.pos = tuple(pos)
        self.futurePositions = []
        self.futureVelocities = []
        self.futureBounces = []
        self.originatingPlayer = player
        self.vel = tuple(velocity)
        self.timeLeft = lifetime
        self.kind = kind
        self.expired = False
        self.justFired = True
        self.hasBounced = False

    def checkCollision(self, player):
        if player.isFriendsWith(self.originatingPlayer):
            return False
        return self.checkCollisionsWithPoints(player.oldPos, player.pos)

    def checkCollisionsWithPoints(self, oldPos, newPos, ticksInFuture=0):
        '''
        Checks whether a player moving between the given points will collide
        with this shot. If futureTicks is given, it is the number of ticks
        in the future (for this shot) that we are checking these points.
        '''
        oldShotPos, newShotPos = self.getFuturePoints(ticksInFuture)
        if oldShotPos is None:
            # Shot has expired
            return False

        # Check both player colliding with us and us colliding with player
        if collideTrajectory(
                newPos, oldShotPos,
                (newShotPos[0] - oldShotPos[0], newShotPos[1] - oldShotPos[1]),
                self.playerCollisionTolerance):
            return True

        deltaX = newPos[0] - oldPos[0]
        deltaY = newPos[1] - oldPos[1]
        if collideTrajectory(
                newShotPos, oldPos, (deltaX, deltaY),
                self.playerCollisionTolerance):
            return True
        return False

    def hitPlayer(self, player, hitpoints):
        self.expired = True
        player.onHitByShot(self)
        self.originatingPlayer.onShotHitSomething(self)
        self.onExpire()
        if hitpoints:
            self.originatingPlayer.onShotHurtPlayer(player, self)

    def getFuturePoints(self, ticksInFuture=0):
        '''
        @return: (oldPos, newPos) for a tick the given number of ticks in
            the future, or (None, None) if the shot has expired by that
            time. Calls extendFuturePositions() if needed.
        '''
        if self.expired:
            return None, None
        if ticksInFuture == 0:
            return self.oldPos, self.pos
        ticksLeft = self.timeLeft // self.world.tickPeriod + 1
        if ticksInFuture > ticksLeft:
            return None, None

        while len(self.futurePositions) < ticksInFuture:
            if self.futureHasExpired():
                return None, None
            self.extendFuturePositions()

        if ticksInFuture < 2:
            assert ticksInFuture == 1
            oldPos = self.pos
        else:
            oldPos = self.futurePositions[ticksInFuture - 2]
        newPos = self.futurePositions[ticksInFuture - 1]
        if newPos is None:
            oldPos = None
        return oldPos, newPos

    def futureHasExpired(self):
        if self.expired:
            return True
        return self.futurePositions and self.futurePositions[-1] is None

    def getFutureVelocity(self):
        if self.futureVelocities:
            return self.futureVelocities[-1]
        return self.vel

    def extendFuturePositions(self):
        unit = copy.copy(self)
        unit.oldPos, unit.pos = self.getFuturePoints(len(self.futurePositions))
        unit.vel = self.getFutureVelocity()

        deltaT = self.world.tickPeriod
        delta = (unit.vel[0] * deltaT, unit.vel[1] * deltaT)
        unit.pos, collision = self.world.physics.getMotion(
            unit, delta, ignoreLedges=True)

        bouncePos = None
        expired = False
        if collision:
            if self.kind == Shot.RICOCHET:
                bouncePos = unit.pos
                self.rebound(unit, collision)
            else:
                expired = True

        self.futurePositions.append(unit.pos)
        self.futureVelocities.append(unit.vel)
        if expired:
            self.futurePositions.append(None)
            self.futureVelocities.append(unit.vel)
        if bouncePos is not None:
            self.futureBounces.append((len(self.futurePositions), bouncePos))

    def advance(self):
        '''
        Called by the universe when this shot should update its position.
        '''
        if self.expired:
            return
        self.justFired = False

        deltaT = self.world.tickPeriod

        oldPos, pos = self.getFuturePoints(ticksInFuture=1)
        if self.futurePositions:
            self.futurePositions.pop(0)
            self.vel = self.futureVelocities.pop(0)
            if self.futureBounces:
                for i, (t, pos) in enumerate(self.futureBounces):
                    self.futureBounces[i] = (max(0, t - 1), pos)

                t, pos = self.futureBounces[0]
                if t == 0:
                    self.futureBounces.pop(0)
                    self.hasBounced = True
                    self.onRebound(pos)

        # Shots have a finite lifetime.
        self.timeLeft = self.timeLeft - deltaT

        if pos is None:
            self.expired = True
            self.onExpire()
        else:
            self.pos = pos

    def rebound(self, unit, collision):
        '''
        Shot is a ricochet shot and it's hit an obstacle.
        '''
        obsAngle = collision.angle
        shotAngle = atan2(unit.vel[1], unit.vel[0])
        dif = shotAngle - obsAngle
        final = obsAngle - dif
        speed = sqrt(unit.vel[0] * unit.vel[0] + unit.vel[1] * unit.vel[1])
        unit.vel = (speed * cos(final), speed * sin(final))


class LocalShot(LocalSprite, Shot):
    def advance(self):
        self.justFired = False
        super(LocalShot, self).advance()


class PredictedRicochetTrajectory(PredictedTrajectory):

    collisionShape = Shot.collisionShape

    def __init__(self, world, player):
        self.world = world
        self.player = player

    def predictedTrajectoryPoints(self):
        shot = self.player.createShot(shotClass=LocalShot)
        if shot.kind is None:
            # Cannot shoot at present (e.g. on wall)
            return

        i = 0
        while True:
            _, pos = shot.getFuturePoints(i)
            if pos is None:
                return
            yield pos
            i += 1


class PredictedGhostShotTrajectory(PredictedTrajectory):

    RADIUS = Shot.RADIUS

    def __init__(self, world, player, viewManager):
        self.world = world
        self.player = player
        self.viewManager = viewManager

    def getAngle(self, playerPos=None):
        if playerPos is None:
            livePlayer = self.player.clone()
            livePlayer.respawn()
            playerPos = livePlayer.pos

        focus = self.viewManager._focus
        area = self.viewManager.sRect
        playerScreenPos = mapPosToScreen(playerPos, focus, area)
        targetPos = pygame.mouse.get_pos()
        return atan2(
            targetPos[0] - playerScreenPos[0],
            -(targetPos[1] - playerScreenPos[1]))

    def predictedTrajectoryPoints(self):
        livePlayer = self.player.clone()
        livePlayer.respawn()
        livePlayer.lookAt(self.getAngle(livePlayer.pos))
        shot = livePlayer.createShot(shotClass=LocalShot)
        if shot.kind is None:
            # Cannot shot at present (e.g. on wall)
            return

        i = 0
        while True:
            _, pos = shot.getFuturePoints(i)
            if pos is None:
                return
            yield pos
            i += 1
