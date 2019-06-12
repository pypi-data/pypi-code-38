

import copy
import logging
import math
from math import sin, cos, pi, atan2
import struct

from trosnoth.const import (
    OFF_MAP_DEATH_HIT, DEFAULT_RESYNC_MESSAGE, HOOK_BREAK_SPEED,
    HOOK_ATTACHED, DEFAULT_COIN_VALUE, HOOK_EXTEND_SPEED, HOOK_RETRACT_SPEED,
    DEATH_TAX_RATE, DEATH_TAX_FREE_THRESHOLD, DEATH_MAX_COIN_COUNT,
    HOOK_FIRING, HOOK_NOT_ACTIVE, HOOK_RETURNING, HOOK_LENGTH,
    TICK_PERIOD, LEFT_STATE, RIGHT_STATE, JUMP_STATE,
    ALIVE_STATE, ALL_DEAD_STATE, PHANTOM_STATE, BOMBER_DEATH_HIT, DOWN_STATE,
    HOOK_PULL_PLAYER_SPEED, EMOTE_BOOGIE, EMOTE_CHARLESTON, EMOTE_WAVE,
    HEAD_CUEBALL,
)
from trosnoth.model.physics import CollisionEllipse, CollisionCircle
from trosnoth.model.shot import Shot
from trosnoth.model.unit import Unit
from trosnoth.model.universe_base import NEUTRAL_TEAM_ID
from trosnoth.model.upgrades import (
    ItemManager, Bomber, MachineGun, Shield,
    PhaseShift, Shoxwave, Ricochet, Ninja, MinimapDisruption,
)
from trosnoth.utils.event import Event
from trosnoth.utils.math import (
    distance, isNear, moveTowardsPointAndReturnEndPoint, RotatedAxes,
)
from trosnoth.utils.unrepr import unrepr

from trosnoth.messages import (
    PlayerUpdateMsg, ResyncPlayerMsg, ChatFromServerMsg, ResyncAcknowledgedMsg,
    GrapplingHookMsg,
)

RESPAWN_CAMP_TIME = 1.0
MAX_RESYNC_TIME = 10    # seconds
GRIP_TIME = 0.1
MAX_FLOOR_ANGLE = pi / 2
MIN_ROOF_ANGLE = pi / 2
WALL_ANGLE_VARIANCE = 0.1   # radians
GROUND_ADHERENCE_RATE = 400     # units/sec
GRAPPLING_GRAB_RANGE = 20   # units

log = logging.getLogger(__name__)


class PlayerInputState:
    def __init__(
            self, left=False, right=False, jump=False, drop=False,
            hook=False, angle=0, thrust=0):
        self.left = left
        self.right = right
        self.jump = jump
        self.drop = drop
        self.hook = hook
        self.angle = angle
        self.thrust = thrust

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return (self.left == other.left and self.right == other.right and
                self.jump == other.jump and self.drop == other.drop and
                self.hook == other.hook and isNear(self.angle, other.angle)
                and isNear(self.thrust, other.thrust))

    def __str__(self):
        init = type(self).__init__
        defaults = init.__defaults__
        bits = []
        for i in range(1, len(init.__code__.co_varnames)):
            key = init.__code__.co_varnames[i]
            default = init.__defaults__[i - 1]
            value = getattr(self, key)
            if value != default:
                bits.append('{}={}'.format(key, value))
        return '{}({})'.format(type(self).__name__, ', '.join(bits))


class Player(Unit):
    '''Maintaint the state of a player. This could be the user's player, a
    player on the network, or conceivably even a bot.
    '''

    HALF_WIDTH = 10
    HALF_HEIGHT = 19

    Y_MID_TO_SHOULDERS = 1
    X_MID_TO_BACKBONE = 0
    X_SHOULDERS_TO_GUN = 10
    Y_SHOULDERS_TO_GUN = 13

    collisionShape = CollisionEllipse(HALF_WIDTH, HALF_HEIGHT)

    def __init__(
            self, world, nick, team, id, dead=False, bot=False,
            head=HEAD_CUEBALL, *args, **kwargs):
        super(Player, self).__init__(world, *args, **kwargs)

        self.world = world

        self.onDied = Event(['killer', 'deathType'])
        self.onAllDead = Event([])
        self.onKilled = Event(['target', 'deathType', 'hadItems'])
        self.onCoinsChanged = Event(['oldCoins'])
        self.onNeutralisedSector = Event()  # (zoneCount)
        self.onTaggedZone = Event()         # (zone, previousOwner)
        self.onUsedUpgrade = Event()        # (upgrade)
        self.onUpgradeGone = Event()        # (upgrade)
        self.onShotFired = Event()          # (shot)
        self.onShotHurtPlayer = Event()     # (target, shot)
        self.onHitByShot = Event()          # (shot)
        self.onShieldDestroyed = Event()    # (shooter, deathType)
        self.onDestroyedShield = Event()    # (target, deathType)
        self.onPrivateChatReceived = Event()    # (text, sender)
        self.onGotTrosball = Event()
        self.onCoinsSpent = Event()         # (coins)
        self.onRespawned = Event([])
        self.onShotHitSomething = Event()   # (shot)
        self.onOverlayDebugHook = Event()   # (viewManager, screen, sprite)
        self.onTeamSet = Event()
        self.onRemovedFromGame = Event(['playerId'])
        self.onJoinComplete = Event([])

        # Identity
        self.nick = nick
        self.head = head
        self.agent = None
        self.team = team
        self.id = id
        self.bot = bot
        self.joinComplete = False

        # Preferences during the voting phase.
        self.preferredTeam = ''
        self.readyToStart = False
        self.preferredSize = (0, 0)
        self.preferredDuration = 0
        self.preferredLevel = b'auto'

        # Input state
        self._state = {LEFT_STATE:  False,
                       RIGHT_STATE: False,
                       JUMP_STATE:  False,
                       DOWN_STATE: False,
        }
        self.ignoreState = set()
        self.grapplingHook = GrapplingHook(self)

        # Physics
        self._jumpTime = 0.0
        self.xVel = 0
        self.yVel = 0
        self.angleFacing = 1.57
        self.ghostThrust = 0.0      # Determined by mouse position
        self._faceRight = True
        self.reloadTime = 0.0
        self.reloadFrom = 0.0
        self.timeTillRespawn = 0.0
        self.nextRespawnTime = None
        self.invulnerableUntil = None
        self.gripCountDown = 0
        self.grabbedSurfaceAngle = None
        self._cachedGroundCollision = None
        self._cachedGroundCollisionKey = None

        # Flag to say that the last attempt to advance the player was not
        # allowed, either due to the zone being unenterable or the motion
        # leaving the map.
        self.movementProhibited = False

        self.items = ItemManager(self)
        self.emote = None

        # Other state info
        self.coins = 0
        if dead:
            self.health = 0
            self.lifeState = ALL_DEAD_STATE
        else:
            self.health = self.world.physics.playerRespawnHealth
            self.lifeState = ALIVE_STATE
        self.resyncing = False
        self.resyncExpiry = None
        self.lastResyncMessageSent = None   # Server only

    def clone(self):
        '''
        Used to create the local representation of this player object.
        '''
        result = copy.copy(self)
        result._state = copy.copy(self._state)
        result.ignoreState = copy.copy(self.ignoreState)
        result.grapplingHook = self.grapplingHook.clone(result)
        result.items = ItemManager(result)
        result.items.restore(self.items.dump())
        result.emote = copy.copy(self.emote)
        result.lastResyncMessageSent = None
        result.onDied = Event(['killer', 'deathType'])
        result.onAllDead = Event([])
        result.onKilled = Event(['target', 'deathType', 'hadItems'])
        result.onCoinsChanged = Event(['oldCoins'])
        result.onNeutralisedSector = Event()
        result.onTaggedZone = Event()
        result.onUsedUpgrade = Event()
        result.onUpgradeGone = Event()
        result.onShotFired = Event()
        result.onShotHurtPlayer = Event()
        result.onHitByShot = Event()
        result.onShieldDestroyed = Event()
        result.onDestroyedShield = Event()
        result.onPrivateChatReceived = Event()
        result.onGotTrosball = Event()
        result.onCoinsSpent = Event()
        result.onRespawned = Event([])
        result.onShotHitSomething = Event()
        result.onOverlayDebugHook = Event()
        result.onTeamSet = Event()
        result.onRemovedFromGame = Event(['playerId'])
        result.onJoinComplete = Event([])
        return result

    def dump(self):
        '''
        Returns a serialised dump of the player object for newly
        connected players
        '''
        return {
            'id': self.id,
            'teamId': self.teamId,
            'nick': self.nick,
            'head': self.head,
            'bot': self.bot,
            'update': self.getPlayerUpdateArgs(),
            'items': self.items.dump(),
            'preferences': {
                'team': self.preferredTeam,
                'size': self.preferredSize,
                'duration': self.preferredDuration,
                'ready': self.readyToStart,
            },
        }

    def restore(self, data):
        '''
        Restores the player state based on the given serialised player dump
        :param data: Output of the player dump
        '''
        team = self.world.teamWithId[data['teamId']]
        bot = data['bot']
        update = data['update']
        preferences = data['preferences']

        self.nick = data['nick']
        self.head = data['head']
        self.team = team
        self.bot = bot

        self.items.restore(data['items'])

        self.applyPlayerUpdate(PlayerUpdateMsg(*update))

        self.preferredTeam = preferences['team']
        self.preferredSize = tuple(preferences['size'])
        self.preferredDuration = preferences['duration']
        self.readyToStart = preferences['ready']
        self.onTeamSet()

    def isCanonicalPlayer(self):
        return self in self.world.players

    @property
    def user(self):
        if self.agent:
            return self.agent.user
        return None

    @property
    def dead(self):
        return self.lifeState != ALIVE_STATE

    @property
    def allDead(self):
        '''
        It's possible for a player to be dead and not know it (e.g. killed by
        grenade or shoxwave and hasn't yet received the network message). It
        this case the easiest way to keep the server and client in sync is by
        treating it as a ghost that moves like a living player.
        '''
        return self.lifeState == ALL_DEAD_STATE

    def willNotChangeOnNextTick(self):
        '''
        :return: true iff, in its current state, the player will not move when
            a tick message comes.
        '''
        if self.oldPos != self.pos:
            return False
        if not self.allDead:
            if not self.isStationary():
                return False
            if self.items.hasAny():
                return False
            if self.reloadTime != 0:
                return False
            if self.emote:
                return False
        else:
            if self.timeTillRespawn != 0:
                return False
            if self.ghostThrust != 0:
                return False
        return True

    def isStationary(self):
        '''
        :return: true iff the player is currently not moving and is either on
            the ground, or hanging from a wall/roof.
        '''
        if not (isNear(self.xVel, 0) and isNear(self.yVel, 0)):
            return False
        if self.getGrapplingHook().isActive():
            return False
        return self.isGrabbingWall() or bool(self.getGroundCollision())

    def getXKeyMotion(self):
        if self._state[LEFT_STATE] and not self._state[RIGHT_STATE]:
            return -1
        if self._state[RIGHT_STATE] and not self._state[LEFT_STATE]:
            return 1
        return 0

    def hasTrosball(self):
        manager = self.world.trosballManager
        return (
            manager.enabled and manager.trosballPlayer
            and manager.trosballPlayer.id == self.id)

    @property
    def identifyingName(self):
        if self.user is None:
            return self.nick
        return self.user.username

    def hasVisibleShield(self):
        return self.items.has(Shield)

    def getTotalHitPoints(self):
        result = self.health
        shield = self.items.get(Shield)
        if shield:
            result += shield.protections
        return result

    @property
    def phaseshift(self):
        return self.items.get(PhaseShift)

    @property
    def shoxwave(self):
        return self.items.get(Shoxwave)

    @property
    def machineGunner(self):
        return self.items.get(MachineGun)

    @property
    def hasRicochet(self):
        return self.items.get(Ricochet)

    @property
    def ninja(self):
        return self.items.get(Ninja)

    @property
    def disruptive(self):
        return self.items.get(MinimapDisruption)

    @property
    def bomber(self):
        return self.items.get(Bomber)

    @property
    def canMove(self):
        return not (self.bomber or self.emote)

    @property
    def invisible(self):
        if self.ninja:
            if self.reloadTime != 0.0:
                return False
            if self.distanceFromZoneCentre() > 200:
                return True
            zone = self.getZone()
            if zone and self.isFriendsWithTeam(zone.owner):
                return True
            return False
        return False

    def distanceFromZoneCentre(self):
        zone = self.getZone()
        if not zone:
            return 2000
        return distance(zone.defn.pos, self.pos)

    def isFriendsWith(self, other):
        '''
        Returns True iff self and other are on the same team.
        '''
        if other.id == self.id:
            return True
        return self.isFriendsWithTeam(other.team)

    def isFriendsWithTeam(self, team):
        if team is None:
            return False
        return self.team == team

    def inRespawnableZone(self):
        zone = self.getZone()
        return self.isZoneRespawnable(zone)

    def isZoneRespawnable(self, zone):
        if not zone:
            return False
        return self.team is None or zone.owner == self.team

    @property
    def teamId(self):
        if self.team is None:
            return NEUTRAL_TEAM_ID
        return self.team.id

    @property
    def teamName(self):
        if self.team is None:
            return self.world.rogueTeamName
        return self.team.teamName

    def isEnemyTeam(self, team):
        '''
        Returns True iff the given team is an enemy team of this player. It is
        not enough for the team to be neutral (None), it must actually be an
        enemy for this method to return True.
        '''
        if team is None:
            return False
        return self.team != team

    def isInvulnerable(self):
        iu = self.invulnerableUntil
        if iu is None:
            return False
        elif self.world.getMonotonicTime() > iu:
            self.invulnerableUntil = None
            return False
        return True

    def isHurtByShots(self):
        if self.isInvulnerable() or self.phaseshift:
            return False
        return True

    @property
    def isMinimapDisrupted(self):
        for team in self.world.teams:
            if team != self.team and team.usingMinimapDisruption:
                return True
        return False

    def setPos(self, pos):
        self.pos = self.oldPos = pos

    def __str__(self):
        return self.nick

    def getDetailsForLeaderBoard(self):
        if self.id == -1:
            return {}

        pID = struct.unpack('B', self.id)[0]
        nick = self.nick
        team = self.teamId
        dead = self.dead
        coins = self.coins

        if self.world.scoreboard and self.world.scoreboard.playerScoresEnabled:
            score = self.world.scoreboard.playerScores[self]
        else:
            score = None

        return {
            'pID': pID,
            'nick': nick,
            'team': team,
            'dead': dead,
            'coins': coins,
            'bot': self.bot,
            'ready': self.readyToStart,
            'score': score,
        }

    def removeFromGame(self):
        '''Called by network client when server says this player has left the
        game.'''

        self.items.clear()

        if self.hasTrosball():
            self.world.trosballManager.playerDroppedTrosball()

    def continueOffMap(self):
        if self.world.isServer and not self.dead:
            self.world.sendKill(self, OFF_MAP_DEATH_HIT, None)
        return False

    def canEnterZone(self, newZone):
        if newZone == self.getZone():
            return True
        world = self.world
        if world.abilities.leaveFriendlyZones:
            return True

        if newZone is None:
            if self.dead:
                # Pre-game ghost cannot leave map
                return False
        elif newZone.owner != self.team:
            return False

        return True

    def updateState(self, key, value):
        '''Update the state of this player. State information is information
        which is needed to calculate the motion of the player. For a
        human-controlled player, this is essentially only which keys are
        pressed. Keys which define a player's state are: left, right, jump and
        down.
        Shooting is processed separately.'''

        if self.resyncing:
            return
        self.ignoreState.discard(key)

        # Set the state.
        self._state[key] = value

    def getState(self, key):
        return self._state[key]

    def setInputState(self, inputState):
        self.updateState(LEFT_STATE, inputState.left)
        self.updateState(RIGHT_STATE, inputState.right)
        self.updateState(JUMP_STATE, inputState.jump)
        self.updateState(DOWN_STATE, inputState.drop)

        self.lookAt(inputState.angle, inputState.thrust)
        if GrapplingHookMsg(inputState.hook, 0).validate(self):
            self.getGrapplingHook().setState(inputState.hook)

    def checkMotionKey(self, key):
        return (self._state[key] and key not in self.ignoreState)

    def lookAt(self, angle, thrust=None):
        '''Changes the direction that the player is looking.  angle is in
        radians and is measured clockwise from vertical.'''

        if self.resyncing:
            return

        if thrust is not None:
            self.ghostThrust = min(1, max(0, thrust))

        angle = (angle + pi) % (2 * pi) - pi
        if self.angleFacing == angle:
            return

        self.angleFacing = angle
        self._faceRight = angle > 0

    def isFacingRight(self):
        return self._faceRight

    def activateItemByCode(self, upgradeType, local=None):
        upgradeClass = self.world.getUpgradeType(upgradeType)
        return self.items.activate(upgradeClass, local)

    def updateGhost(self):
        deltaT = self.world.tickPeriod
        self.timeTillRespawn = max(0, self.timeTillRespawn - deltaT)

        magnitude = (
            self.world.physics.playerMaxGhostVel * deltaT * self.ghostThrust)
        finalPos = (
            self.pos[0] + magnitude * sin(self.angleFacing),
            self.pos[1] - magnitude * cos(self.angleFacing),
        )

        if self.canMoveToPos(finalPos):
            self.pos = finalPos
        else:
            self.movementProhibited = True

    def canMoveToPos(self, pos):
        if not self.world.map.isInMap(pos):
            if not self.continueOffMap():
                return False
        else:
            newZone = self.world.map.getZoneAtPoint(pos)
            if not self.canEnterZone(newZone):
                return False
        return True

    def getGroundIntentionAndDirection(self):
        '''
        Returns intent, direction where direction is -1 for left and +1 for
        right, and intent is -1 for slow down, 0 for walk and 1 for run.
        '''
        if not self.canMove:
            keySpeed = 0
        elif self._state[LEFT_STATE] and not self._state[RIGHT_STATE]:
            if self._faceRight:
                keySpeed = -1
            else:
                keySpeed = -2
        elif self._state[RIGHT_STATE] and not self._state[LEFT_STATE]:
            if self._faceRight:
                keySpeed = +2
            else:
                keySpeed = +1
        else:
            keySpeed = 0

        if self.xVel < 0:
            dir = -1
        elif self.xVel > 0:
            dir = +1
        elif keySpeed < 0:
            dir = -1
        elif keySpeed > 0:
            dir = +1
        else:
            return 0, 0

        if dir * keySpeed == +2:
            intent = 1
        elif dir * keySpeed == +1:
            intent = 0
        else:
            intent = -1

        return intent, dir

    def getAirAcceleration(self):
        if not self.canMove:
            return 0, False

        physics = self.world.physics

        if self.grapplingHook.isAttached():
            if self._state[LEFT_STATE] and not self._state[RIGHT_STATE]:
                if self.xVel > -physics.playerMaxHookDodgeSpeed:
                    return -physics.playerAirAcceleration, False
            elif self._state[RIGHT_STATE] and not self._state[LEFT_STATE]:
                if self.xVel < physics.playerMaxHookDodgeSpeed:
                    return physics.playerAirAcceleration, False

        elif self._state[LEFT_STATE] and not self._state[RIGHT_STATE]:
            if self.xVel > -physics.playerMaxAirDodgeSpeed:
                return -physics.playerAirAcceleration, False

        elif self._state[RIGHT_STATE] and not self._state[LEFT_STATE]:
            if self.xVel < physics.playerMaxAirDodgeSpeed:
                return physics.playerAirAcceleration, False

        else:
            if self.xVel > 0:
                return -physics.playerAirAcceleration, True
            elif self.xVel < 0:
                return physics.playerAirAcceleration, True

        return 0, False

    def getCurrentVelocity(self):
        '''
        Used to decide how fast the Trosball should go if it's dropped.
        '''
        return (self.xVel, self.yVel)

    def updateLivingPlayer(self):
        groundCollision = self.getGroundCollision()
        self.processJumpState(groundCollision)
        self.checkForWallRelease()
        self.applyVelocityThresholdsAndAcceleration(groundCollision)
        self.constrainVelocityByGrapplingHook()
        motionCollision = self.applyVelocity()
        if motionCollision:
            self.dampCollisionNormalVelocity(motionCollision)
        if groundCollision:
            self.adhereToGround()
        self.grapplingHook.updateHookPosition()
        self.grapplingHook.afterPlayerMovement()
        self.fixEdgeVelocity()
        self.discretiseLocation()

    def fixEdgeVelocity(self):
        if isNear(self.yVel, 0):
            self.yVel = 0
        if isNear(self.xVel, 0):
            self.xVel = 0

    def getGrapplingHook(self):
        return self.grapplingHook

    def getGrapplingHookPos(self):
        return self.grapplingHook.oldPos, self.grapplingHook.pos

    def applyVelocityThresholdsAndAcceleration(self, groundCollision):
        '''
        Adjust the player's velocity for one tick.
        If this player is initiating a jump, run, or push off a wall,
        this method applies the appropriate initial instantaneous velocity
        minimum to the player.
        This method then applies one tick's worth of this player's current
        acceleration based on gravity and the keys pressed.
        '''
        physics = self.world.physics
        deltaT = self.world.tickPeriod

        if self.isGrabbingWall():
            self.xVel = self.yVel = 0
            return

        applyGravity = True
        if groundCollision:
            self.applyGroundMotion(groundCollision)
            if not self.grapplingHook.isAttached():
                applyGravity = False
        else:
            xAccel, limited = self.getAirAcceleration()
            oldXVel = self.xVel
            self.xVel += deltaT * xAccel
            if limited and oldXVel * self.xVel < 0:
                if abs(self.xVel) < physics.playerAirSmallSpeed:
                    self.xVel = 0

        if applyGravity:
            self.yVel = self.yVel + self.world.physics.playerGravity * deltaT
            self.yVel = min(self.yVel, self.world.physics.playerMaxFallVel)

        if self._jumpTime > 0:
            self.yVel = -self.world.physics.playerJumpThrust
            self._jumpTime = max(0, self._jumpTime - deltaT)

    def applyGroundMotion(self, groundCollision):
        physics = self.world.physics
        deltaT = self.world.tickPeriod
        intention, direction = self.getGroundIntentionAndDirection()
        isRunning = (intention > 0)
        isSlowing = (intention < 0)

        self.grabbedSurfaceAngle = None

        collision = groundCollision
        for i in range(3):
            axes = RotatedAxes(collision.angle)
            testVector = axes.globalFromRotated((direction, 0))
            collision = self.getMinisculeCollision(testVector)
            if not collision:
                break
            if not -MAX_FLOOR_ANGLE < collision.angle < MAX_FLOOR_ANGLE:
                break
        else:
            self.xVel = self.yVel = 0
            return

        sVel, tVel = axes.rotatedFromGlobal((self.xVel, self.yVel))
        if isRunning:
            if abs(sVel) < physics.playerXVel:
                sVel = physics.playerXVel * direction
            sVel += direction * physics.playerRunAcceleration * deltaT
            sVel = min(sVel, physics.playerMaxRunSpeed)
            sVel = max(sVel, -physics.playerMaxRunSpeed)
        else:
            sVel -= direction * physics.playerRunDeceleration * deltaT
            if isSlowing:
                if sVel * direction < 0:
                    sVel = 0
            else:
                if sVel * direction < physics.playerSlowXVel:
                    sVel = direction * physics.playerSlowXVel
        self.xVel, self.yVel = axes.globalFromRotated((sVel, tVel))

    def processJumpState(self, groundCollision):
        '''
        Checks the player's jump key state to decide whether to initiate a jump
        or stop a jump.
        '''
        if bool(groundCollision) or self.isGrabbingWall():
            self.gripCountDown = GRIP_TIME
        else:
            self.gripCountDown = max(0, self.gripCountDown - TICK_PERIOD)
        canStartJump = self.gripCountDown > 0
        jumpKeyDown = self.checkMotionKey(JUMP_STATE) and self.canMove

        if not jumpKeyDown:
            self._jumpTime = 0
            # You can't have an upward y-velocity if you're not pressing the
            # up key. This was originally so that stopping jumping would be
            # responsive, but the way it interacts with the grappling hook
            # feels pretty nice so we're leaving it in.
            self.yVel = max(0, self.yVel)
        elif canStartJump:
            # Initiate the jump
            self._jumpTime = self.world.physics.playerMaxJumpTime

    def getGroundCollisionCacheKey(self):
        return (self.pos, self.checkMotionKey(DOWN_STATE))

    def getGroundCollision(self):
        cacheKey = self.getGroundCollisionCacheKey()
        if self._cachedGroundCollisionKey != cacheKey:
            self._cachedGroundCollision = self.getMinisculeCollision((0, 1))
            self._cachedGroundCollisionKey = cacheKey
        return self._cachedGroundCollision

    def getMinisculeCollision(self, vector, dist=0.5):
        '''
        Returns the collision that would occur if this player moved a small
        distance (default 0.1 units) in the direction of the given vector.
        '''
        x, y = vector
        magnitude = (x ** 2 + y ** 2) ** 0.5
        if magnitude < 0.001:
            return None
        scale = dist / magnitude
        return self.getCollision((x * scale, y * scale))

    def getCollision(self, vector):
        downPressed = self.checkMotionKey(DOWN_STATE)
        return self.world.physics.getCollision(
            self, vector, ignoreLedges=downPressed)

    def isPullingAgainstGrapplingHook(self):
        '''
        Return True iff the player is pressing the left or right arrow key that
        would pull away from where the grappling hook is attached.
        '''
        hook = self.grapplingHook
        if not hook.isAttached():
            return
        if hook.pos[0] > self.pos[0]:
            return self.checkMotionKey(LEFT_STATE)
        return self.checkMotionKey(RIGHT_STATE)

    def constrainVelocityByGrapplingHook(self):
        '''
        If this player has a grappling hook currently attached to something,
        this method will update the player's velocity to ensure that the
        player is being pulled towards the grappling hook's anchor point at
        the appropriate velocity.
        '''
        hook = self.grapplingHook
        if not hook.isAttached():
            return
        axes = RotatedAxes(hook.getPullAngle())

        sVel, tVel = axes.rotatedFromGlobal((self.xVel, self.yVel))
        pull_speed = HOOK_PULL_PLAYER_SPEED

        modified = False
        hookDistance = distance(hook.pos, self.pos)
        if sVel < pull_speed:
            if self.isPullingAgainstGrapplingHook():
                # Release hook to allow player to continue moving
                if pull_speed - sVel > HOOK_BREAK_SPEED:
                    hook.setState(False)
                    return

            # Constrain to pull/release speed
            speedToEndPoint = hookDistance / self.world.tickPeriod
            if pull_speed > speedToEndPoint:
                tVel = 0
                sVel = speedToEndPoint
            else:
                sVel = pull_speed
            modified = True

        sVelFullLength = (HOOK_LENGTH - hookDistance) / self.world.tickPeriod
        if sVel < -sVelFullLength:
            # Constrain to maximum rope length
            sVel = -sVelFullLength
            modified = True

        if modified:
            xVel, yVel = axes.globalFromRotated((sVel, tVel))
            if self.isPullingAgainstGrapplingHook() and self.xVel * xVel < 0:
                # Release hook rather than having x-velocity change sign
                hook.setState(False)
            else:
                self.xVel = xVel
                self.yVel = yVel

    def constrainVelocityToSurface(self, collision):
        '''
        If this player is touching a surface, this method will make sure
        that the player's current velocity does not push the player through
        the surface.
        '''
        isRoof = not (-MIN_ROOF_ANGLE <= collision.angle <= MIN_ROOF_ANGLE)
        if isRoof and not self.grapplingHook.isAttached():
            self._jumpTime = 0
            self.yVel = max(self.yVel, 0)

        axes = RotatedAxes(collision.angle)
        sVel, tVel = axes.rotatedFromGlobal((self.xVel, self.yVel))
        self.xVel, self.yVel = axes.globalFromRotated((sVel, 0))

        return collision

    def getPlayerMotion(self):
        '''
        :return: (finalPos, collision) for moving one tick's worth of
            distance based on this player's current velocity.
        '''
        if abs(self.xVel) < 0.5:
            self.xVel = 0
        if abs(self.yVel) < 0.5:
            self.yVel = 0

        deltaT = self.world.tickPeriod
        deltaX = self.xVel * deltaT
        deltaY = self.yVel * deltaT

        return self.getMotion(deltaX, deltaY)

    def getMotion(self, deltaX, deltaY):
        downPressed = self.checkMotionKey(DOWN_STATE)
        return self.world.physics.getMotion(
            self, (deltaX, deltaY),
            ignoreLedges=downPressed)

    def applyVelocity(self):
        '''
        Applies one tick's worth of the player's current velocity to the
        player's position. If there is an obstacle in the player's path,
        only moves the player as far as the obstacle, and zeroes any
        component of the velocity that goes into the surface of the obstacle.
        '''

        finalPos, collision = self.getPlayerMotion()
        if collision and collision.travelDistance < 0.5:
            # Already touching this surface. Constrain velocity to the surface.
            self.constrainVelocityToSurface(collision)
            if self.checkForWallGrab(collision):
                self.wallIsNowGrabbed(collision.angle)
                return collision

            # Try again, moving along the surface
            finalPos, collision = self.getPlayerMotion()

            if collision and collision.travelDistance < 0.5:
                # Wedged between two surfaces
                if self.checkForWallGrab(collision):
                    self.wallIsNowGrabbed(collision.angle)
                else:
                    self.xVel = self.yVel = 0
                return collision

        if self.canMoveToPos(finalPos):
            self.pos = finalPos
        else:
            self.movementProhibited = True

        if self.checkForWallGrab(collision):
            self.wallIsNowGrabbed(collision.angle)
        elif collision:
            self.constrainVelocityToSurface(collision)

        return collision

    def dampCollisionNormalVelocity(self, collision):
        # Damp velocity in direction normal to surface
        axes = RotatedAxes(collision.angle)
        sVel, tVel = axes.rotatedFromGlobal((self.xVel, self.yVel))
        self.xVel, self.yVel = axes.globalFromRotated((sVel, 0))

    def checkForWallGrab(self, collision):
        if not collision:
            return False

        if self.grapplingHook.isAttached():
            if distance(collision.contactPoint, self.grapplingHook.pos
                    ) < GRAPPLING_GRAB_RANGE:
                self.grapplingHook.reset()
                if abs(collision.angle) >= MAX_FLOOR_ANGLE:
                    return True
        elif isNear(collision.angle, pi / 2, WALL_ANGLE_VARIANCE):
            if not collision.ledge and self.checkMotionKey(LEFT_STATE):
                return True
        elif isNear(collision.angle, -pi / 2, WALL_ANGLE_VARIANCE):
            if not collision.ledge and self.checkMotionKey(RIGHT_STATE):
                return True
        return False

    def wallIsNowGrabbed(self, collisionAngle):
        self.grabbedSurfaceAngle = collisionAngle
        self.xVel = self.yVel = 0
        for state in (LEFT_STATE, RIGHT_STATE, JUMP_STATE):
            if self.checkMotionKey(state):
                self.ignoreState.add(state)

    def checkForWallRelease(self):
        if not self.isGrabbingWall():
            return

        if (
                self.checkMotionKey(DOWN_STATE)
                or self.checkMotionKey(LEFT_STATE)
                or self.checkMotionKey(RIGHT_STATE)
                or self.checkMotionKey(JUMP_STATE)
                or not self.canMove):
            self.grabbedSurfaceAngle = None

    def isGrabbingWall(self):
        return self.grabbedSurfaceAngle is not None

    def adhereToGround(self):
        tryingToJump = (self._jumpTime > 0)
        if tryingToJump or self.grapplingHook.isAttached():
            return

        deltaT = self.world.tickPeriod
        deltaY = deltaT * GROUND_ADHERENCE_RATE
        finalPos, collision = self.getMotion(0, deltaY)
        if collision:
            self.pos = finalPos

            # Constrain the velocity to the new surface
            axes = RotatedAxes(collision.angle)
            sVel, tVel = axes.rotatedFromGlobal((self.xVel, self.yVel))
            self.xVel, self.yVel = axes.globalFromRotated((sVel, 0))

    def discretiseLocation(self):
        '''
        In order for the bot motion to work, the map needs to have a finite
        number of stationary locations. This method looks up whether there's a
        canonical stationary location near the player's current location,
        and moves them there if the player is stationary.
        '''
        if not self.isStationary():
            return

        pathFinder = self.world.map.layout.pathFinder
        if self.isGrabbingWall():
            grabAngle = self.grabbedSurfaceAngle
        else:
            grabAngle = self.getGroundCollision().angle
        pos, angle = pathFinder.getDiscreteLocation(self.pos, grabAngle)
        if pos is None:
            return
        self.setDiscreteLocation(pos, angle)

    def setDiscreteLocation(self, pos, angle):
        self.pos = pos
        self.xVel = self.yVel = 0
        if not (self.getGroundCollision()
                and -MAX_FLOOR_ANGLE < angle < MAX_FLOOR_ANGLE):
            # Not on the ground, so must be on wall or roof
            self.wallIsNowGrabbed(angle)

    # For debugging
    _lastAdvanceState = None

    def advance(self):
        '''Called by this player's universe when this player should update
        its position. deltaT is the time that's passed since its state was
        current, measured in seconds.'''
        self._lastAdvanceState = self.getPlayerUpdateArgs()

        self.movementProhibited = False

        if self.resyncing:
            return

        self.items.tick()
        if self.emote:
            if self.emote.tick():
                self.emote = None
        self.reloadTime = max(0.0, self.reloadTime - self.world.tickPeriod)

        if self.allDead:
            self.updateGhost()
        else:
            self.updateLivingPlayer()

    def isOnside(self, trosballPosition):
        onLeftOfBall = self.pos[0] < trosballPosition[0]
        onBlueTeam = self.team == self.world.teams[0]
        return onLeftOfBall == onBlueTeam

    def hit(self, hitpoints, hitter, hitKind):
        if hitpoints <= 0:
            return

        shield = self.items.get(Shield)
        if shield:
            hitpoints = shield.hit(hitpoints, hitter, hitKind)
            if hitpoints <= 0:
                return
        self.health -= hitpoints

        if self.health <= 0:
            self.died(hitter, hitKind)

    def died(self, killer, hitKind):
        self.health = 0
        self.lifeState = PHANTOM_STATE
        self.timeTillRespawn = self.world.physics.playerRespawnTotal
        if hitKind == BOMBER_DEATH_HIT:
            self.nextRespawnTime = self.world.physics.bomberRespawnTime
        else:
            self.nextRespawnTime = None

        if self.isCanonicalPlayer():
            if self.hasTrosball():
                self.world.trosballManager.playerDroppedTrosball()
            if self.hasElephant():
                self.world.elephantKill(killer)
            self.world.playerHasDied(self, killer, hitKind)

            if killer:
                killer.onKilled(
                    self, hitKind, hadItems=self.items.getActiveKinds())
            self.world.onPlayerKill(killer, self, hitKind)
        self.onDied(killer, hitKind)

    def makeAllDead(self, respawnTime=None):
        '''
        Called in response to PlayerAllDeadMsg.
        '''
        self.health = 0
        self.lifeState = ALL_DEAD_STATE
        if respawnTime is not None:
            self.timeTillRespawn = respawnTime
            self.nextRespawnTime = None
        elif self.nextRespawnTime:
            self.timeTillRespawn = self.nextRespawnTime
            self.nextRespawnTime = None
        else:
            self.timeTillRespawn = self.world.physics.playerRespawnTotal
        self._jumpTime = 0
        self.gripCountDown = 0
        self.grabbedSurfaceAngle = None
        self.items.clear()
        self.emote = None
        self.grapplingHook.reset()
        self.onAllDead()

    def returnToLife(self):
        self.health = self.world.physics.playerRespawnHealth
        self.lifeState = ALIVE_STATE
        self.timeTillRespawn = 0
        self.xVel = 0
        self.yVel = 0
        self.gripCountDown = 0
        self.grabbedSurfaceAngle = None

    def respawn(self, zone=None):
        if self.resyncing:
            return
        self.returnToLife()
        self.invulnerableUntil = (
            self.world.getMonotonicTime() + RESPAWN_CAMP_TIME)
        self.teleportToZoneCentre(zone)
        if self.isCanonicalPlayer():
            self.world.onPlayerRespawn(self)
        self.onRespawned()

    def doEmote(self, emoteId):
        self.emote = Emote(emoteId)

    def teleportToZoneCentre(self, zone=None):
        if zone is None:
            zone = self.getZone()
        self.setPos(zone.defn.pos)

    def incrementCoins(self, count):
        oldCoins = self.coins
        self.coins += count
        self.onCoinsChanged(oldCoins)

    def setCoins(self, count):
        oldCoins = self.coins
        self.coins = count
        self.onCoinsChanged(oldCoins)

    def getValueToDropOnDeath(self):
        taxableCoins = max(0, self.coins - DEATH_TAX_FREE_THRESHOLD)
        valueToDrop = int(taxableCoins * DEATH_TAX_RATE + 0.5)
        return valueToDrop

    def getCoinDisplayCount(self):
        valueToDrop = self.getValueToDropOnDeath()
        return min(DEATH_MAX_COIN_COUNT, int(valueToDrop / DEFAULT_COIN_VALUE))

    def getCoinsToDropOnDeath(self):
        valueToDrop = self.getValueToDropOnDeath()
        count = self.getCoinDisplayCount()

        if count == DEATH_MAX_COIN_COUNT:
            for i in range(count - 1):
                yield DEFAULT_COIN_VALUE
                valueToDrop -= DEFAULT_COIN_VALUE
            yield valueToDrop
        else:
            remaining = count
            while remaining:
                thisCoin = int(valueToDrop / remaining + 0.5)
                yield thisCoin
                valueToDrop -= thisCoin
                remaining -= 1

    def getShotType(self):
        '''
        Returns one of the following:
            None - if the player cannot currently shoot
            'N' - if the player can shoot normal shots
            'R' - if the player can shoot ricochet shots
        '''
        if self.dead or self.phaseshift or not self.canMove:
            return None

        if self.team and not self.team.abilities.aggression:
            return None

        if self.reloadTime > 0:
            return None

        if self.hasRicochet:
            return Shot.RICOCHET
        return Shot.NORMAL

    def isElephantOwner(self):
        return self.user is not None and self.user.ownsElephant

    def hasElephant(self):
        playerWithElephant = self.world.playerWithElephant
        return playerWithElephant and playerWithElephant.id == self.id

    def canShoot(self):
        return self.getShotType() is not None

    def sendResync(self, reason=DEFAULT_RESYNC_MESSAGE, error=False):
        if not self.world.isServer:
            raise TypeError('Only servers can send resync messages')

        if self.resyncing and self.stateHasNotChangedSinceResyncSent():
            return

        args = self.getPlayerUpdateArgs(resync=bool(self.agent))
        globalMsg, resyncMsg = PlayerUpdateMsg(*args), ResyncPlayerMsg(*args)
        self.world.sendServerCommand(globalMsg)
        if self.agent:
            self.lastResyncMessageSent = resyncMsg
            self.agent.messageToAgent(resyncMsg)
            if reason:
                # Perhaps we should default to error=True, but these are too
                # common at present
                self.agent.messageToAgent(ChatFromServerMsg(
                    error=error, text=reason.encode('utf-8')))
        self.resyncBegun()

    def stateHasNotChangedSinceResyncSent(self):
        if self.lastResyncMessageSent is None:
            return False
        comparison = ResyncPlayerMsg(*self.getPlayerUpdateArgs())
        return comparison.pack() == self.lastResyncMessageSent.pack()

    def resyncBegun(self):
        self.resyncing = True
        self.resyncExpiry = self.world.getMonotonicTick() + int(
            MAX_RESYNC_TIME / self.world.tickPeriod)

    def getPlayerUpdateArgs(self, resync=None):
        if resync is None:
            resync = self.resyncing

        if self.grabbedSurfaceAngle is None:
            grabbedSurfaceAngle = math.nan
        else:
            grabbedSurfaceAngle = self.grabbedSurfaceAngle
        grapplingHookState = repr(self.grapplingHook.dump()).encode('utf-8')

        return (
            self.id, self.pos[0], self.pos[1], self.xVel, self.yVel,
            self.angleFacing,
            self.ghostThrust, self._jumpTime, self.reloadTime,
            self.timeTillRespawn, self.coins, self.health, resync,
            self._state[LEFT_STATE], self._state[RIGHT_STATE],
            self._state[JUMP_STATE], self._state[DOWN_STATE],
            LEFT_STATE in self.ignoreState,
            RIGHT_STATE in self.ignoreState,
            JUMP_STATE in self.ignoreState,
            DOWN_STATE in self.ignoreState,
            self.gripCountDown, grabbedSurfaceAngle,
            self.emote.emoteId if self.emote else 0,
            self.emote.ticksRemaining if self.emote else 0,
            grapplingHookState,
        )

    def applyPlayerUpdate(self, msg):
        self._state[LEFT_STATE] = msg.leftKey
        self._state[RIGHT_STATE] = msg.rightKey
        self._state[JUMP_STATE] = msg.jumpKey
        self._state[DOWN_STATE] = msg.downKey
        self.ignoreState.clear()
        if msg.ignoreLeft:
            self.ignoreState.add(LEFT_STATE)
        if msg.ignoreRight:
            self.ignoreState.add(RIGHT_STATE)
        if msg.ignoreJump:
            self.ignoreState.add(JUMP_STATE)
        if msg.ignoreDown:
            self.ignoreState.add(DOWN_STATE)

        self.xVel = msg.xVel
        self.yVel = msg.yVel
        self.lookAt(msg.angle, msg.ghostThrust)
        self.setPos((msg.xPos, msg.yPos))
        self._jumpTime = msg.jumpTime
        self.reloadTime = msg.gunReload
        self.timeTillRespawn = msg.respawn
        oldCoins = self.coins
        self.coins = msg.coins
        self.gripCountDown = msg.gripCountDown
        if math.isnan(msg.grabbedSurfaceAngle):
            self.grabbedSurfaceAngle = None
        else:
            self.grabbedSurfaceAngle = msg.grabbedSurfaceAngle
        self.health = msg.health
        if self.health > 0:
            self.lifeState = ALIVE_STATE
        else:
            self.lifeState = ALL_DEAD_STATE
            self._jumpTime = 0
            self.gripCountDown = 0
            self.grabbedSurfaceAngle = None
            self.items.clear()

        if msg.resync:
            self.resyncBegun()
        else:
            self.resyncing = False
        if oldCoins != self.coins:
            self.onCoinsChanged(oldCoins)

        if self.lifeState == ALL_DEAD_STATE:
            self.grapplingHook.reset()
        else:
            self.grapplingHook.restore(
                unrepr(msg.grapplingHookState.decode('utf-8')))

        if msg.emoteTicks <= 0:
            self.emote = None
        else:
            self.emote = Emote(msg.emoteId)
            self.emote.ticksRemaining = msg.emoteTicks

    def buildResyncAcknowledgement(self):
        return ResyncAcknowledgedMsg(
            self.world.lastTickId, self.pos[0], self.pos[1],
            self.yVel, self.angleFacing, self.ghostThrust, self.health)

    def checkResyncAcknowledgement(self, msg):
        '''
        Checks whether the player position etc. matches the position encoded in
        the ResyncPlayerMsg or ResyncAcknowledgedMsg.
        '''
        return (
            isNear(self.pos[0], msg.xPos)
            and isNear(self.pos[1], msg.yPos)
            and isNear(self.yVel, msg.yVel)
            and isNear(self.angleFacing, msg.angle)
            and isNear(self.ghostThrust, msg.ghostThrust)
            and msg.health == self.health)

    def weaponDischarged(self):
        '''
        Updates the player's reload time because the player has just fired a
        shot.
        '''
        world = self.world
        zone = self.getZone()
        if self.machineGunner:
            reloadTime = self.machineGunner.weaponDischarged()
        elif self.shoxwave:
            reloadTime = world.physics.playerShoxwaveReloadTime
        elif self.team is None:
            reloadTime = world.physics.playerNeutralReloadTime
        elif world.trosballManager.enabled:
            if (
                    abs(self.pos[0] - world.trosballManager.getPosition()[0])
                    < 1e-5):
                reloadTime = world.physics.playerNeutralReloadTime
            # If self is on blue, and on the left of the trosball; or
            # completely vice versa
            elif self.isOnside(world.trosballManager.getPosition()):
                reloadTime = world.physics.playerOwnDarkReloadTime
            else:
                reloadTime = world.physics.playerEnemyDarkReloadTime
        elif zone and zone.owner == self.team and zone.dark:
            reloadTime = world.physics.playerOwnDarkReloadTime
        elif zone and not zone.dark:
            reloadTime = world.physics.playerNeutralReloadTime
        else:
            reloadTime = world.physics.playerEnemyDarkReloadTime
        self.reloadTime = self.reloadFrom = reloadTime

    def createShot(self, shotId=None, shotClass=Shot):
        '''
        Factory function for building a Shot object.
        '''
        # Shots take some fraction of the player's current velocity, but we
        # still want the shots to always go directly towards where the user
        # clicked, so we take the component of player velocity in the direction
        # of the shot.
        f = self.world.physics.fractionOfPlayerVelocityImpartedToShots
        xVel = (self.pos[0] - self.oldPos[0]) / self.world.tickPeriod
        yVel = (self.pos[1] - self.oldPos[1]) / self.world.tickPeriod
        shotVel = self.world.physics.shotSpeed + f * (
            xVel * sin(self.angleFacing) - yVel * cos(self.angleFacing))

        velocity = (
            shotVel * sin(self.angleFacing),
            -shotVel * cos(self.angleFacing),
        )

        kind = self.getShotType()
        lifetime = self.world.physics.shotLifetime
        x = self.pos[0] + self.X_SHOULDERS_TO_GUN * sin(self.angleFacing)
        if self.isFacingRight():
            x -= self.X_MID_TO_BACKBONE
        else:
            x += self.X_MID_TO_BACKBONE
        y = self.pos[1]
        y -= self.Y_MID_TO_SHOULDERS
        y -= self.Y_SHOULDERS_TO_GUN * cos(self.angleFacing)

        team = self.team
        shot = shotClass(
            self.world, shotId, team, self, (x, y), velocity, kind, lifetime)
        return shot

    def buildStateChanges(self, desiredState):
        result = []
        for k, v in list(self._state.items()):
            desired = desiredState.get(k, False)
            if v != desired:
                result.append((k, desired))
        return result


class GrapplingHookDummyUnit(Unit):
    collisionShape = CollisionCircle(1)


class GrapplingHook(object):
    def __init__(self, player):
        self.player = player
        self.world = player.world
        self.pos = None
        self.corners = []
        self.launchVelocity = None
        self.oldPos = None
        self.hookState = HOOK_NOT_ACTIVE
        self.unit = GrapplingHookDummyUnit(self.world)
        self._retractingLength = None

    def clone(self, player):
        result = copy.copy(self)
        result.player = player
        return result

    def dump(self):
        if self.hookState == HOOK_NOT_ACTIVE:
            return {}
        return {
            'lv': self.launchVelocity,
            'p': self.pos,
            's': self.hookState,
            'c': self.corners,
        }

    def restore(self, data):
        if not data:
            self.reset()
            return
        self.launchVelocity = data['lv']
        self.pos = data['p']
        self.oldPos = self.pos
        self.hookState = data['s']
        self.corners = data['c']

    def reset(self):
        self.pos = None
        self.corners = []
        self.launchVelocity = None
        self.oldPos = None
        self.hookState = HOOK_NOT_ACTIVE

    def setState(self, active):
        if active:
            self._doActivate()
        else:
            self._doRelease()

    def _doActivate(self):
        xVel = HOOK_EXTEND_SPEED * sin(self.player.angleFacing)
        yVel = HOOK_EXTEND_SPEED * -cos(self.player.angleFacing)
        self.launchVelocity = (xVel, yVel)
        self.corners = []
        self.pos = self.oldPos = self.player.pos
        self.hookState = HOOK_FIRING

    def _doRelease(self):
        if self.hookState != HOOK_NOT_ACTIVE:
            self.hookState = HOOK_RETURNING

    def isActive(self):
        return self.hookState in (HOOK_FIRING, HOOK_ATTACHED)

    def isAttached(self):
        return self.hookState == HOOK_ATTACHED

    def isReturning(self):
        return self.hookState == HOOK_RETURNING

    def getPullAngle(self):
        pX, pY = self.player.pos
        hX, hY = self.pos
        return atan2(hY - pY, hX - pX)

    def updateHookPosition(self):
        self._retractingLength = None
        self.oldPos = self.pos
        if not self.player.canMove:
            self._doRelease()

        if self.hookState == HOOK_FIRING:
            self._extendHook()
        elif self.hookState == HOOK_RETURNING:
            self._retractHook()

    def _extendHook(self):
        x, y = self.pos
        xVel, yVel = self.launchVelocity
        deltaT = self.world.tickPeriod

        self.unit.pos = self.pos
        motion = (xVel * deltaT, yVel * deltaT)
        endPos, collision = self.world.physics.getMotion(self.unit, motion)
        self.pos = endPos
        if collision:
            self.hookState = HOOK_ATTACHED
            self.player.grabbedSurfaceAngle = None

    def _retractHook(self):
        self._retractingLength = self._getLength() \
                                 - HOOK_RETRACT_SPEED * self.world.tickPeriod

    def afterPlayerMovement(self):
        if self.hookState not in (HOOK_FIRING, HOOK_RETURNING):
            return
        self._detectHookCorners()
        self._checkForEndPoint()

    def _detectHookCorners(self):
        # TODO
        pass

    def _checkForEndPoint(self):
        if self.hookState == HOOK_FIRING:
            maxLength = HOOK_LENGTH
        else:
            maxLength = self._retractingLength

        curLength = self._getLength()
        if curLength > maxLength:
            self._shortenBy(curLength - maxLength)
            if self.hookState == HOOK_FIRING:
                self.hookState = HOOK_RETURNING

    def _getLength(self):
        points = [self.pos] + self.corners + [self.player.pos]
        i = 0
        length = 0
        while i + 1 < len(points):
            length += distance(points[i], points[i + 1])
            i += 1
        return length

    def _shortenBy(self, dist):
        points = [self.pos] + self.corners + [self.player.pos]
        while True:
            thisLength = distance(points[0], points[1])
            if dist < thisLength:
                points[0] = moveTowardsPointAndReturnEndPoint(
                    points[0], points[1], dist, 1)
                self.pos = points[0]
                self.corners = points[1:-1]
                return

            dist -= thisLength
            points.pop(0)
            if len(points) == 1:
                self.reset()
                return


class Emote:
    SPRITE_SEQUENCE = {
        EMOTE_BOOGIE: [(i, 11) for i in range(6)],
        EMOTE_CHARLESTON: [(i, 11) for i in (8, 7, 6, 7, 8, 9, 10, 9)],
        EMOTE_WAVE: [(i, 11) for i in range(11, 17)],
    }
    FRAME_RATE = {
        EMOTE_BOOGIE: 0.12,
        EMOTE_CHARLESTON: 0.08,
        EMOTE_WAVE: 0.08,
    }

    def __init__(self, emoteId):
        self.emoteId = emoteId
        self.ticksRemaining = 30

    @property
    def spriteIndices(self):
        return self.SPRITE_SEQUENCE[self.emoteId]

    @property
    def frameRate(self):
        return self.FRAME_RATE[self.emoteId]

    @property
    def timeRemaining(self):
        return self.ticksRemaining * TICK_PERIOD

    def tick(self):
        self.ticksRemaining -= 1
        return self.ticksRemaining <= 0
