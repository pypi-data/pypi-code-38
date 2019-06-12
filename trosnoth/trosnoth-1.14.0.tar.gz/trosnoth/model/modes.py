'''
modes.py: defines a set of pre-defined game modes
'''

import logging

log = logging.getLogger(__name__)


class PhysicsConstants(object):
    STATE_ATTRS = [
        'normal',
        'shooting',
        'shotSpeed',
        'shotLifetime',
        'fractionOfPlayerVelocityImpartedToShots',
        'playerXVel',
        'playerSlowXVel',
        'playerMaxGhostVel',
        'playerJumpThrust',
        'playerMaxFallVel',
        'playerMaxJumpTime',
        'playerGravity',
        'playerOwnDarkReloadTime',
        'playerNeutralReloadTime',
        'playerEnemyDarkReloadTime',
        'playerMachineGunReloadTime',
        'playerMachineGunFireRate',
        'playerShotHeat',
        'playerRespawnTotal',
        'playerBounce',
        'playerRespawnHealth',
        'playerShoxwaveReloadTime',
        'grenadeMaxFallVel',
        'grenadeGravity',
        'grenadeInitVel',
        'trosballThrowVel',
        'trosballExplodeTime',
    ]

    def __init__(self):
        self.setModeNormal()

    def hasMode(self, gameMode):
        return hasattr(self, 'setMode' + gameMode)

    def setMode(self, gameMode):
        try:
            fn = getattr(self, 'setMode' + gameMode)
        except (AttributeError, TypeError):
            return False

        fn()
        return True

    def _standard(self, pace=1, fireRate=1, gravity=1, jumpHeight=1,
            respawnRate=1, shotSpeed=1, shotLength=1, bounce=False,
            respawnHealth=1, shooting=True, trosballTime=5, shotFactor=1,
            normal=False, playerDampingFactor=0.3):

        self.normal = normal
        self.shooting = shooting
        self.playerDampingFactor = playerDampingFactor

        # Speed that shots travel at.
        self.shotSpeed = 600 * shotSpeed                      # pix/s
        self.shotLifetime = (1. / shotSpeed) * shotLength     # s
        self.fractionOfPlayerVelocityImpartedToShots = 0.3 * shotFactor

        # The following values control player movement.
        self.playerXVel = 360 * pace                  # pix/s
        self.playerSlowXVel = 180 * pace              # pix/s
        self.playerRunAcceleration = 650 * pace       # pix/s/s
        self.playerRunDeceleration = 4000 * pace      # pix/s/s
        self.playerMaxRunSpeed = 650 * pace           # pix/s
        self.playerAirAcceleration = 2000 * pace      # pix/s/s
        self.playerMaxAirDodgeSpeed = 360 * pace      # pix/s
        self.playerMaxHookDodgeSpeed = 720 * pace     # pix/s
        self.playerAirSmallSpeed = 60 * pace          # pix/s
        self.playerMaxGhostVel = 1300 * pace          # pix/s
        self.playerJumpThrust = 540 * jumpHeight      # pix/s
        self.playerMaxFallVel = 700. * gravity        # pix/s
        self.playerMaxJumpTime = 0.278                # s
        self.playerGravity = 3672 * gravity           # pix/s/s
        self.playerOwnDarkReloadTime = 1 / 2.7 / fireRate      # s
        self.playerNeutralReloadTime = 1 / 2. / fireRate   # s
        self.playerEnemyDarkReloadTime = 1 / 1.4 / fireRate    # s
        self.playerMachineGunReloadTime = 4 / fireRate   # s
        self.playerMachineGunFireRate = 0.1 / fireRate   # s
        self.playerShotHeat = 0.4
        self.playerRespawnTotal = 7.5 / respawnRate
        self.bomberRespawnTime = self.playerRespawnTotal * 0.4
        self.playerBounce = bounce
        self.playerRespawnHealth = respawnHealth
        self.playerShoxwaveReloadTime = self.playerEnemyDarkReloadTime

        self.grenadeMaxFallVel = 700. * gravity
        self.grenadeGravity = 300 * gravity
        self.grenadeInitVel = 500 * pace
        self.trosballThrowVel = 1000 * pace

        self.trosballExplodeTime = trosballTime

        # For calculation of cost of shortest path
        xMax = max(self.playerXVel, self.playerSlowXVel)
        yMax = max(self.playerMaxFallVel, self.playerJumpThrust)
        self.maxLivePlayerSpeed = (xMax ** 2 + yMax ** 2) ** 0.5

    def dumpState(self):
        return {k: getattr(self, k) for k in self.STATE_ATTRS}

    def restoreState(self, data):
        for k, v in data.items():
            if k in self.STATE_ATTRS:
                setattr(self, k, v)

    def setModeNoShots(self):
        self._standard(shooting=False)

    def setModeLightning(self):
        self._standard(pace=1.75, fireRate=2)

    def setModeLowGravity(self):
        self._standard(gravity=0.25)

    def setModeNormal(self):
        self._standard(normal=True)

    def setModeFastFire(self):
        self._standard(fireRate=3, shotSpeed=2)

    def setModeInsane(self):
        self._standard(pace=1.75, fireRate=3, jumpHeight=2, shotSpeed=2,
                        shotLength=2, respawnRate=60)

    def setModeFastRespawn(self):
        self._standard(respawnRate=60)

    def setModeSlow(self):
        self._standard(pace=0.5, gravity=0.25, jumpHeight=0.7, shotSpeed=0.5)

    def setModeHighFastFall(self):
        self._standard(jumpHeight=2, gravity=2)

    def setModeLaser(self):
        self._standard(shotSpeed=30, shotLength=100)

    def setModeManyShots(self):
        self._standard(shotLength=20)

    def setModeZeroG(self):
        self._standard(gravity=0.001)

    def setModeAntiG(self):
        self._standard(gravity=-0.1)

    def setModeBouncy(self):
        self._standard(bounce=True)

    def setModeHighBouncy(self):
        self._standard(bounce=True, jumpHeight=3)

    def setModeTwoLives(self):
        self._standard(respawnHealth=2)

    def setRapidTrosball(self):
        self._standard(trosballTime=1)

    def setModeTenHealth(self):
        self._standard(respawnHealth=10, fireRate=2.5)

    def setModeFiveHealth(self):
        self._standard(respawnHealth=5, fireRate=2.5)
