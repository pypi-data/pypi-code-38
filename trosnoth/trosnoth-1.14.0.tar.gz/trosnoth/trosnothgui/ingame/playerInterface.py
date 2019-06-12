import logging
from math import atan2, sin, cos

import pygame

from trosnoth.const import (
    ACTION_LEFT, ACTION_RIGHT, ACTION_JUMP, ACTION_DOWN, ACTION_HOOK,
    ACTION_RESPAWN, ACTION_USE_UPGRADE, MAP_TO_SCREEN_SCALE,
    LEFT_STATE, RIGHT_STATE, JUMP_STATE, DOWN_STATE,
    ACTION_SHOW_TRAJECTORY, ACTION_DEBUGKEY,
)
from trosnoth.gui.framework import framework
from trosnoth.gui.keyboard import mouseButton
from trosnoth.messages import (
    UpdatePlayerStateMsg, AimPlayerAtMsg, ShootMsg, GrapplingHookMsg,
)
from trosnoth.model.shot import PredictedRicochetTrajectory
from trosnoth.utils import globaldebug
from trosnoth.utils.math import distance, isNear

log = logging.getLogger(__name__)


class TickInstructions(object):
    def __init__(self):
        self.state = {}
        self.angleFacing = None
        self.ghostThrust = None
        self.firedGun = False

    def updateState(self, key, value):
        self.state[key] = value

    def lookAt(self, angle, thrust):
        self.angleFacing = angle
        self.ghostThrust = thrust

    def applyTo(self, player):
        for key, value in self.state.items():
            if player.getState(key) == value:
                if not value:
                    continue
                player.updateState(key, False)
            player.updateState(key, value)

        if self.angleFacing is not None:
            player.lookAt(self.angleFacing, self.ghostThrust)

        if self.firedGun:
            player.weaponDischarged()


class PlayerInterface(framework.Element):
    '''Interface for controlling a player.'''

    # The virtual keys we care about.
    state_vkeys = {
        ACTION_LEFT: LEFT_STATE,
        ACTION_RIGHT: RIGHT_STATE,
        ACTION_JUMP: JUMP_STATE,
        ACTION_DOWN: DOWN_STATE,
    }

    NO_GHOST_THRUST_MOUSE_RADIUS = 50       # pixels
    FULL_GHOST_THRUST_MOUSE_RADIUS = 250    # pixels

    def __init__(self, app, gameInterface):
        super(PlayerInterface, self).__init__(app)

        world = gameInterface.world
        self.gameInterface = gameInterface
        self.keyMapping = None
        self._stateKeys = None
        self._hookKey = None
        self.keyMappingUpdated()

        self.receiving = True

        self.world = world
        self.worldGui = gameInterface.gameViewer.worldgui

        self.mousePos = (0, 0)
        self.discardOneMouseRel = True

        # Make sure the viewer is focusing on this player.
        self.gameInterface.gameViewer.setTarget(self.playerSprite)

    def keyMappingUpdated(self):
        self.keyMapping = self.gameInterface.keyMapping
        self._stateKeys = {
            (self.keyMapping.getkey(vkey), state)
            for vkey, state in self.state_vkeys.items()
        }
        self._hookKey = self.keyMapping.getkey(ACTION_HOOK)

    def getTickId(self):
        return self.world.lastTickId

    def stop(self):
        pass

    @property
    def player(self):
        return self.gameInterface.localState.player

    @property
    def playerSprite(self):
        return self.worldGui.getPlayerSprite(self.player.id)

    def tick(self, deltaT):
        if self.player is None:
            # Can happen just after PlayerInterface is removed
            return

        self.updateMouse()
        self.updatePlayerViewAngle()
        if self.player.canShoot():
            if self.player.machineGunner and self.player.machineGunner.firing:
                self._fireShot()

        # Sometimes Pygame seems to miss some keyboard events, so double
        # check here.
        if not self.gameInterface.detailsInterface.chatBox.isOpen():
            keys = pygame.key.get_pressed()
            desiredState = {
                code: keys[key] for key, code in self._stateKeys
                if key >= 0}
            changes = self.player.buildStateChanges(desiredState)
            for code, value in changes:
                self.gameInterface.sendRequest(UpdatePlayerStateMsg(
                    value, stateKey=code, tickId=self.getTickId()))
                log.critical('Sent missing player state update: %r / %r',
                    code, value)
            if self._hookKey >= 0 and not keys[self._hookKey] and \
                    self.player.getGrapplingHook().isActive():
                self.gameInterface.sendRequest(
                    GrapplingHookMsg(False, self.getTickId()))

    def updateMouse(self):
        spritePos = self.playerSprite.rect.center
        pos = pygame.mouse.get_pos()
        self.mousePos = (pos[0] - spritePos[0], pos[1] - spritePos[1])

    def updatePlayerViewAngle(self):
        '''Updates the viewing angle of the player based on the mouse pointer
        being at the position pos. This gets its own method because it needs
        to happen as the result of a mouse motion and of the viewManager
        scrolling the screen.'''
        if self.world.uiOptions.showPauseMessage:
            return

        if self.player and self.player.dead and \
                self.gameInterface.detailsInterface.trajectoryOverlay.enabled:

            # Move ghost towards the orb
            pos0 = self.player.pos
            zone = self.player.getZone()
            if zone is None:
                theta = 0
                dist = 0
            else:
                pos1 = zone.defn.pos
                theta = atan2(pos1[0] - pos0[0], -(pos1[1] - pos0[1]))
                dist = distance(pos0, pos1) * MAP_TO_SCREEN_SCALE
        else:
            dx, dy = self.mousePos
            pos = (self.playerSprite.rect.center[0] + dx,
                   self.playerSprite.rect.center[1] + dy)

            if self.playerSprite.rect.collidepoint(pos):
                return

            # Angle is measured clockwise from vertical.
            theta = atan2(dx, -dy)
            dist = (dx ** 2 + dy ** 2) ** 0.5

        # Calculate a thrust value based on distance.
        if dist < self.NO_GHOST_THRUST_MOUSE_RADIUS:
            thrust = 0.0
        elif dist > self.FULL_GHOST_THRUST_MOUSE_RADIUS:
            thrust = 1.0
        else:
            span = (
                self.FULL_GHOST_THRUST_MOUSE_RADIUS -
                self.NO_GHOST_THRUST_MOUSE_RADIUS)
            thrust = (dist - self.NO_GHOST_THRUST_MOUSE_RADIUS) / span
            thrust **= 2

        self.gameInterface.sendRequest(
            AimPlayerAtMsg(theta, thrust, tickId=self.getTickId()))

    def processEvent(self, event):
        '''Event processing works in the following way:
        1. If there is a prompt on screen, the prompt will either use the
        event, or pass it on.
        2. If passed on, the event will be sent back to the main class, for it
        to process whether player movement uses this event. If it doesn't use
        the event, it will pass it back.
        3. If so, the hotkey manager will see if the event means anything to
        it.  If not, that's the end, the event is ignored.
        '''

        # Handle events specific to in-game.
        di = self.gameInterface.detailsInterface
        if self.player:
            if event.type == pygame.KEYDOWN:
                self.processKeyEvent(event.key, True)
            elif event.type == pygame.KEYUP:
                self.processKeyEvent(event.key, False)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.player.dead:
                        if di.trajectoryOverlay.isActive():
                            angle = di.trajectoryOverlay \
                                .getTrajectory().getAngle()
                            di.doAction(ACTION_RESPAWN)
                            self.gameInterface.sendRequest(AimPlayerAtMsg(
                                angle, 1.0, tickId=self.getTickId()))
                            self._fireShot()
                        else:
                            di.doAction(ACTION_RESPAWN)
                    elif self.player.machineGunner:
                        self.player.machineGunner.firing = True
                    elif di.trajectoryOverlay.isActive():
                        trajectory = di.trajectoryOverlay.getTrajectory()
                        if isinstance(trajectory, PredictedRicochetTrajectory):
                            self._fireShot()
                        else:
                            di.doAction(ACTION_USE_UPGRADE)
                    else:
                        # Fire a shot.
                        self._fireShot()
                else:
                    self.processKeyEvent(mouseButton(event.button), True)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if self.player.machineGunner:
                        self.player.machineGunner.firing = False
                else:
                    self.processKeyEvent(mouseButton(event.button), False)

            else:
                return event

    def processKeyEvent(self, key, keyDown):
        try:
            action = self.keyMapping[key]
        except KeyError:
            return

        if action == ACTION_HOOK:
            self.gameInterface.sendRequest(
                GrapplingHookMsg(keyDown, self.getTickId()))
            return

        if action == ACTION_SHOW_TRAJECTORY:
            di = self.gameInterface.detailsInterface
            di.trajectoryOverlay.setEnabled(keyDown)
            return

        if __debug__ and action == ACTION_DEBUGKEY and globaldebug.enabled:
            globaldebug.debugKey = keyDown
            return

        if action not in self.state_vkeys:
            return

        self.gameInterface.sendRequest(UpdatePlayerStateMsg(
            keyDown, stateKey=self.state_vkeys[action],
            tickId=self.getTickId()))
        return

    def _fireShot(self):
        '''Fires a shot in the direction the player's currently looking.'''
        if self.world.uiOptions.showPauseMessage:
            return
        self.gameInterface.sendRequest(ShootMsg(self.getTickId()))
