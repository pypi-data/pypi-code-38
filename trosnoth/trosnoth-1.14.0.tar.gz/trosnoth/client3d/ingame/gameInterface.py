

import logging
import random
from math import pi, atan2, copysign
from twisted.internet import reactor, defer

from direct.actor.Actor import Actor
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import TextNode
from direct.interval.MetaInterval import Sequence
from direct.particles.ParticleEffect import ParticleEffect
from direct.showbase.DirectObject import DirectObject
from direct.showbase.MessengerGlobal import messenger
from direct.task import Task
from panda3d.core import (
    AmbientLight, DirectionalLight, TransparencyAttrib, BitMask32,
    TextureStage, NodePath, Plane, Point3, Camera, PointLight,
)

from trosnoth.client3d.base.app import PandaScene
from trosnoth.client3d.base.keyboard import keyDownEvent, keyUpEvent
from trosnoth.client3d.ingame.joincontroller import JoinGameController
from trosnoth.client3d.ingame.utils import mapPosToPanda, mapSizeToPanda
from trosnoth.const import (
    OPEN_CHAT, PRIVATE_CHAT, TEAM_CHAT, TICK_PERIOD, ACTION_LEFT,
    ACTION_RIGHT, ACTION_JUMP, ACTION_DOWN, ACTION_REALLY_QUIT,
    ACTION_JOIN_GAME, ACTION_TERMINAL_TOGGLE, ACTION_EMOTE,
    ACTION_RESPAWN, ACTION_READY, ACTION_PAUSE_GAME,
    ACTION_CLEAR_UPGRADE, COLLECTABLE_COIN_LIFETIME,
    LEFT_STATE, RIGHT_STATE, JUMP_STATE, DOWN_STATE,
    MAX_EMOTE,
)
from trosnoth.data import getPandaPath
from trosnoth.gamerecording.achievementlist import availableAchievements
from trosnoth.materials import (
    getPlayerMaterial, getShotMaterial,
    getMiniMapShotMaterial,
)
from trosnoth.messages import (
    ChatMsg, ShotFiredMsg, CannotJoinMsg, PlayerHasUpgradeMsg,
    ConnectionLostMsg, ShootMsg, EmoteRequestMsg,
    AchievementUnlockedMsg, AimPlayerAtMsg, PlayerIsReadyMsg,
    UpdatePlayerStateMsg, PlaySoundMsg, RespawnRequestMsg,
)
from trosnoth.model.agent import ConcreteAgent
from trosnoth.model.player import Player
from trosnoth.model.universe_base import NEUTRAL_TEAM_ID
from trosnoth.model.upgrades import Bomber
from trosnoth.utils import globaldebug
from trosnoth.utils.event import Event
from trosnoth.utils.math import distance
from trosnoth.utils.twist import WeakCallLater

log = logging.getLogger(__name__)

MAIN_VIEW_ONLY = BitMask32.bit(0)
MINIMAP_ONLY = BitMask32.bit(1)


class PandaUIAgent(ConcreteAgent):
    '''Interface for when we are connected to a game.'''

    achievementDefs = availableAchievements

    def __init__(
            self, app, game, onDisconnectRequest=None,
            onConnectionLost=None, replay=False, authTag=0):
        super(PandaUIAgent, self).__init__(game=game)
        self.app = app
        self.do = DirectObject()
        self.world.onReset.addListener(self.worldReset)
        self.world.onGrenadeExplosion.addListener(self.grenadeExploded)
        self.world.onTrosballExplosion.addListener(self.trosballExploded)
        self.world.onBomberExplosion.addListener(self.trosballExploded)

        self.onDisconnectRequest = Event()
        if onDisconnectRequest is not None:
            self.onDisconnectRequest.addListener(onDisconnectRequest)

        self.onConnectionLost = Event()
        if onConnectionLost is not None:
            self.onConnectionLost.addListener(onConnectionLost)
        self.game = game

        self.joinDialogReason = None

        if replay:
            self.joinController = None
        else:
            self.joinController = JoinGameController(self.app, self, self.game)

        self.joinInProgress = False

        self.pandaScene = None
        self.ready = False
        defer.maybeDeferred(
            game.addAgent, self, authTag=authTag).addCallback(self.addedAgent)

        self.setElements()
        self.acceptEvents()

    def acceptEvents(self):
        self.do.accept(keyDownEvent(ACTION_REALLY_QUIT), self.disconnect)
        self.do.accept(
            keyDownEvent(ACTION_JOIN_GAME), self.spectatorWantsToJoin)
        self.do.accept(
            keyDownEvent(ACTION_TERMINAL_TOGGLE), self.toggleTerminal)
        # TODO: leader board, minimap toggle

    def addedAgent(self, result):
        self.ready = True
        if self.joinController:
            self.joinDialogReason = 'automatic'
            self.joinController.start()

    def spectatorWantsToJoin(self):
        if self.player or not self.joinController:
            return
        self.joinDialogReason = 'from menu'
        self.joinController.maybeShowJoinDialog(autoJoin=True)

    def sendRequest(self, msg):
        if not self.ready:
            # Not yet completely connected to game
            return
        super(PandaUIAgent, self).sendRequest(msg)

    def worldReset(self, *args, **kwargs):
        if self.ready and self.joinController:
            self.joinController.gotWorldReset()

    @ConnectionLostMsg.handler
    def connectionLost(self, msg):
        if self.joinController:
            self.joinController.hide()
        self.onConnectionLost.execute()

    def joined(self, player):
        '''Called when joining of game is successful.'''
        self.pandaScene.setLocalPlayer(self.localState.player)
        self.setElements()

        self.joinController.hide()

    def spectate(self):
        '''
        Called by join controller if user selects to only spectate.
        '''
        self.setElements()
        self.joinController.hide()

    def joinDialogCancelled(self):
        if self.joinDialogReason == 'automatic':
            self.disconnect()
        else:
            self.spectate()

    def stop(self):
        super(PandaUIAgent, self).stop()
        self.do.ignoreAll()
        self.world.onReset.removeListener(self.worldReset)
        self.world.onGrenadeExplosion.removeListener(self.grenadeExploded)
        self.world.onTrosballExplosion.removeListener(self.trosballExploded)
        self.world.onBomberExplosion.removeListener(self.trosballExploded)
        self.app.setPandaScene(None)
        self.pandaScene = None

    def show(self):
        self.pandaScene = GameScene(self)
        self.app.setPandaScene(self.pandaScene)

    def setElements(self):
        self.elements = [
        ]

    def toggleTerminal(self):
        # TODO: toggle terminal
        pass

    def disconnect(self):
        self.onDisconnectRequest.execute()

    def joinGame(self, nick, team, timeout=10):
        if self.joinInProgress:
            return

        if team is None:
            teamId = NEUTRAL_TEAM_ID
        else:
            teamId = team.id

        self.joinInProgress = True
        self.sendJoinRequest(teamId, nick)
        WeakCallLater(timeout, self, '_joinTimedOut')

    def setPlayer(self, player):
        if not player:
            self.lostPlayer()

        super(PandaUIAgent, self).setPlayer(player)

        if player:
            if __debug__ and globaldebug.enabled:
                globaldebug.localPlayerId = player.id

            self.joinInProgress = False
            self.joined(player)

    @CannotJoinMsg.handler
    def joinFailed(self, msg):
        self.joinInProgress = False
        self.joinController.joinFailed(msg.reasonId)

    def _joinTimedOut(self):
        if self.player or not self.joinInProgress:
            return
        self.joinInProgress = False
        self.joinController.joinFailed('timeout')

    def lostPlayer(self):
        self.setElements()

    @PlayerHasUpgradeMsg.handler
    def gotUpgrade(self, msg):
        player = self.world.getPlayer(msg.playerId)
        if player:
            if self.player is None or self.player.isFriendsWith(player):
                self.playSound('buyUpgrade')

            if self.player is not None and self.player.id == msg.playerId:
                if msg.upgradeType == Bomber.upgradeType:
                    messenger.send(keyDownEvent(ACTION_CLEAR_UPGRADE))

        self.defaultHandler(msg)

    def sendPrivateChat(self, player, targetId, text):
        self.sendRequest(ChatMsg(PRIVATE_CHAT, targetId, text=text.encode()))

    def sendTeamChat(self, player, text):
        self.sendRequest(
            ChatMsg(TEAM_CHAT, player.teamId, text=text.encode()))

    def sendPublicChat(self, player, text):
        self.sendRequest(ChatMsg(OPEN_CHAT, text=text.encode()))

    @AchievementUnlockedMsg.handler
    def achievementUnlocked(self, msg):
        player = self.world.getPlayer(msg.playerId)
        if not player:
            return

        if self.player is not None and self.player.id == msg.playerId:
            # TODO: show "Achievement unlocked" display
            pass

    @ShotFiredMsg.handler
    def shotFired(self, msg):
        self.defaultHandler(msg)
        try:
            shot = self.world.getShot(msg.shotId)
        except KeyError:
            return

        self.pandaScene.playDistanceSound('shoot', shot.pos)

    def grenadeExploded(self, pos, radius):
        self.pandaScene.playDistanceSound('explodeGrenade', pos)

    def trosballExploded(self, player):
        self.pandaScene.playDistanceSound('explodeGrenade', player.pos)

    def playSound(self, action, volume=1):
        self.app.soundPlayer.play(action, volume)

    @PlaySoundMsg.handler
    def playSoundFromServerCommand(self, msg):
        self.app.soundPlayer.playFromServerCommand(
            msg.filename.decode('utf-8'))


class GameScene(PandaScene):
    def __init__(self, gameInterface, *args, **kwargs):
        super(GameScene, self).__init__(gameInterface.app, *args, **kwargs)

        self.normals = None
        self.gloss = None
        self.glow = None

        self.blockForegrounds = set()
        self.gameInterface = gameInterface
        self.localState = gameInterface.localState
        self.world = gameInterface.game.world
        self.camTask = None
        self.uiTickTask = None
        self.tweenFraction = 0

        self.planeOfPlay = Plane((0, 1, 0), (0, 0, 0))
        self.localPlayer = None
        self.miniMapCamera = self.reparent(NodePath('miniMapCamera'))

        self.playersAndShotsWatcher = AllPlayersAndShotsWatcher(self)
        self.statusBarOverlay = StatusBarOverlay(self)
        self.respawnNotice = RespawnNoticeWatcher(self)
        self.cameraOperator = CameraOperator(self)
        self.miniMapDisplay = MiniMapDisplay(self)
        self.watchers = [
            ZoneWatcher(self),
            self.miniMapDisplay,
            self.statusBarOverlay,
            self.playersAndShotsWatcher,
            AllCoinsWatcher(self),
            ClockWatcher(self),
            self.respawnNotice,
            self.cameraOperator,
        ]
        self.lowAmbientLight = None
        self.fullAmbientLight = None

    def getMouseTarget(self):
        '''
        Returns the 3D position of the position in the plane of play where the
        mouse is currently pointing, or None if the mouse is not available.
        '''
        mouseWatcher = self.app.panda.mouseWatcherNode
        if not mouseWatcher.hasMouse():
            return None

        cam = self.app.panda.cam
        render = self.app.panda.render

        p1 = Point3()
        p2 = Point3()
        self.app.panda.camLens.extrude(mouseWatcher.getMouse(), p1, p2)

        result = Point3()
        p1 = render.getRelativePoint(cam, p1)
        p2 = render.getRelativePoint(cam, p2)
        if self.planeOfPlay.intersectsLine(result, p1, p2):
            return result
        return None

    def start(self):
        self.app.panda.enableParticles()
        self.setupTextureStages()
        self.setupCamera()
        self.setupLights()
        self.createForegrounds()
        self.createBackground()
        for watcher in self.watchers:
            watcher.start()
        self.world.onReset.addListener(self.worldReset)

    def stop(self):
        self.world.onReset.removeListener(self.worldReset)
        for watcher in reversed(self.watchers):
            watcher.stop()

        if self.camTask:
            self.app.panda.taskMgr.remove(self.camTask)
            self.camTask = None
        if self.uiTickTask:
            self.app.panda.taskMgr.remove(self.uiTickTask)
            self.uiTickTask = None
        self.app.panda.render.clearLight()
        self.removeBlockForegrounds()

        super(GameScene, self).stop()

    def worldReset(self):
        self.removeBlockForegrounds()
        self.createForegrounds()

    def setLocalPlayer(self, player):
        self.localPlayer = player
        for watcher in self.watchers:
            watcher.setLocalPlayer(player)

    def createForegrounds(self):
        for row in self.world.zoneBlocks:
            for block in row:
                self.addBlockForeground(block)

    def removeBlockForegrounds(self):
        while self.blockForegrounds:
            self.blockForegrounds.pop().removeNode()

    def addBlockForeground(self, block):
        if not block.defn.layout:
            return

        # OnscreenImage default scale is from -1 to 1 in x and z
        w, h = mapSizeToPanda(block.defn.rect.size)
        h = abs(h)

        x, y, z = mapPosToPanda(block.defn.pos)
        x += 0.5 * w
        z -= 0.5 * h

        img = OnscreenImage(
            block.defn.layout.getPandaTexture(self.app.panda),
            scale=(0.5 * w, 1, 0.5 * h), pos=(x, y, z))
        img.setLight(self.fullAmbientLight)
        img.reparentTo(self.app.panda.render)
        self.blockForegrounds.add(img)
        if block.defn.layout.reversed:
            img.setTexOffset(TextureStage.getDefault(), 1, 0)
            img.setTexScale(TextureStage.getDefault(), -1, 1)

        img.setTransparency(TransparencyAttrib.MAlpha)

    def setupLights(self):
        panda = self.app.panda

        panda.setBackgroundColor(0.4, 0.4, 0.5, 1)
        panda.render.clearLight()

        lowLight = AmbientLight('ambientLight')
        lowLight.setColor((.2, .2, .2, 1))
        self.lowAmbientLight = self.reparent(NodePath(lowLight))
        self.fullAmbientLight = self.reparent(NodePath(
            AmbientLight('ambientLight')))

        cameraSpotLight = DirectionalLight('directionalLight')
        cameraSpotLight.setDirection((0, 1, 0))
        cameraSpotLight.setColor((0.6, 0.6, 0.6, 1))
        self.cameraSpotLight = self.reparent(
            NodePath(cameraSpotLight), panda.camera)

    def createBackground(self):
        background = self.app.panda.loader.loadModel('sphere.egg')
        background.setTwoSided(True)
        texture = self.app.panda.loader.loadTexture('stars.jpg')
        background.setTexture(texture)
        self.reparent(background, self.app.panda.camera)
        background.setBin('background', 0)
        background.setDepthWrite(False)
        background.setPos((0, 0, 0))
        background.setCompass()
        background.setScale(2)
        background.setLight(self.fullAmbientLight)
        background.hide(BitMask32.allOn())
        background.show(MAIN_VIEW_ONLY)

    def setupTextureStages(self):
        self.normals = TextureStage('normals')
        self.normals.setMode(TextureStage.MNormal)
        self.gloss = TextureStage('gloss')
        self.gloss.setMode(TextureStage.MGloss)

    def setupCamera(self):
        self.app.panda.cam.node().setCameraMask(MAIN_VIEW_ONLY)
        self.uiTickTask = self.app.panda.taskMgr.add(
            self.uiTick, 'uiTickTask', priority=1)
        self.uiTickTask.lastTime = self.uiTickTask.time

    def uiTick(self, task):
        deltaT = task.time - task.lastTime
        task.lastTime = task.time
        self.tweenFraction = self.app.tweener.uiTick(deltaT)
        return Task.cont

    def playDistanceSound(self, sound, pos, scale=1.):
        sx, sy, sz = mapPosToPanda(pos)
        cx, cy, cz = self.app.panda.camera.getPos()

        # If the camera field of view is larger, we want to hear more sound
        scaledDist = distance((cx, cz), (sx, sz)) / abs(cy - sy)

        # Scale from full volume on the screen to 0 roughly a screen away
        dropOff = min(1, max(0, scaledDist - 0.5))
        volume = scale * (1 - dropOff)

        self.app.soundPlayer.play(sound, volume)


class Watcher(object):
    def __init__(self, scene):
        self.scene = scene
        self.app = scene.app
        self.world = scene.world

    def start(self):
        raise NotImplementedError('{}.start()'.format(self.__class__.__name__))

    def stop(self):
        raise NotImplementedError('{}.stop()'.format(self.__class__.__name__))

    def setLocalPlayer(self, player):
        pass


class CameraOperator(Watcher):
    # Camera parameters
    zOffset = 5             # metres

    def start(self):
        self.localPlayer = None
        self.task = self.app.panda.taskMgr.add(
            self.update, 'cameraTask', priority=100)
        self.task.lastTime = self.task.time

        self.xSpeed = OneAxisWheeler()
        self.ySpeed = OneAxisWheeler()
        self.zSpeed = OneAxisWheeler()

        # 53.13 degrees means the distance back from the plane of the game
        # is roughly equal to the width of map that fits in the field of view
        self.app.panda.camLens.setFov(53.13)

        self.placeCamera(
            (self.world.map.layout.centreX, self.world.map.layout.centreY),
            mapField=self.world.map.layout.worldSize,
        )

    def stop(self):
        if self.task:
            self.app.panda.taskMgr.remove(self.task)
            self.task = None

    def setLocalPlayer(self, player):
        self.localPlayer = player

    def update(self, task):
        deltaT = task.time - task.lastTime
        task.lastTime = task.time
        if self.localPlayer:
            self.trackPlayer(self.localPlayer, deltaT)
        else:
            self.followAction(deltaT)

        return Task.cont

    def mapTargetToCameraPosAndTarget(self, mapPoint, mapField):
        aspectRatio = self.app.panda.camLens.getAspectRatio()
        w, h = mapSizeToPanda(mapField)
        # equation relies on 53.13 degree field of view
        distanceBack = max(abs(w), abs(h * aspectRatio))

        x, y, z = mapPosToPanda(mapPoint)
        newPos = (x, y - distanceBack, z + self.zOffset)
        target = (x, y, z)
        return newPos, target

    def placeCamera(self, mapPoint, mapField=(900, 675), deltaT=0):
        '''
        Immediately places the camera looking at the given point and field.
        '''
        camera = self.app.panda.camera
        oldPos = camera.getPos()
        newPos, target = self.mapTargetToCameraPosAndTarget(mapPoint, mapField)
        camera.setPos(newPos)
        camera.lookAt(target)

        self.xSpeed.reset(newPos[0], deltaT)
        self.ySpeed.reset(newPos[1], deltaT)
        self.zSpeed.reset(newPos[2], deltaT)

        self.updateMiniMapCam(target)

    def slideCamera(self, mapPoint, mapField, deltaT):
        '''
        Smoothly pans and zooms the camera from its current position towards
        the given point and field.
        '''
        camera = self.app.panda.camera
        oldPos = camera.getPos()
        idealPos, _ = self.mapTargetToCameraPosAndTarget(mapPoint, mapField)

        x = self.xSpeed.moveTowards(idealPos[0], deltaT)
        y = self.ySpeed.moveTowards(idealPos[1], deltaT)
        z = self.zSpeed.moveTowards(idealPos[2], deltaT)

        camera.setPos((x, y, z))
        lookAt = (x, 0, z - self.zOffset)
        camera.lookAt(lookAt)
        self.updateMiniMapCam(lookAt)

    def updateMiniMapCam(self, target):
        x, y, z = target
        lens = self.scene.miniMapDisplay.camera.getLens()
        aspectRatio = lens.getAspectRatio()

        worldWidth, worldHeight = mapSizeToPanda(
            self.world.map.layout.worldSize)
        worldHeight = abs(worldHeight)
        minWidth = min(worldWidth, 480)
        minHeight = min(worldHeight, 240)
        # equation relies on 53.13 degree field of view
        xField = max(abs(minWidth), abs(minHeight * aspectRatio))
        zField = xField / aspectRatio
        if xField > worldWidth:
            x = 0.5 * worldWidth
        else:
            x = max(0.5 * xField, min(worldWidth - 0.5 * xField, x))
        if zField > worldHeight:
            z = -0.5 * worldHeight
        else:
            z = min(-0.5 * zField, max(-worldHeight + 0.5 * zField, z))

        self.scene.miniMapCamera.setPos((x, y - xField, z))

    def trackPlayer(self, player, deltaT):
        pos = player.tweenPos(self.scene.tweenFraction)
        self.placeCamera(pos, deltaT=deltaT)

    def followAction(self, deltaT):
        f = self.scene.tweenFraction
        positions = [p.tweenPos(f) for p in self.world.players if not p.dead]
        if not positions:
            positions = [p.tweenPos(f) for p in self.world.players]
            if not positions:
                positions = [(0, 0), self.world.map.layout.worldSize]

        x0 = min(x for (x, y) in positions)
        x1 = max(x for (x, y) in positions)
        y0 = min(y for (x, y) in positions)
        y1 = max(y for (x, y) in positions)

        focus = (0.5 * (x0 + x1), 0.5 * (y0 + y1))
        mapField = (512 + x1 - x0, 384 + y1 - y0)
        self.slideCamera(focus, mapField, deltaT)


class OneAxisWheeler(object):
    '''
    Used for smooth camera motion. In one dimension, moves from current
    position towards a target position.
    '''
    def __init__(self, value=0, maxSpeed=200, acceleration=80):
        self.value = value
        self.velocity = 0
        self.maxSpeed = maxSpeed
        self.acceleration = acceleration

    def reset(self, value, deltaT):
        if deltaT == 0:
            self.velocity = 0
        else:
            self.velocity = (value - self.value) / deltaT
        self.value = value

    def moveTowards(self, target, deltaT):
        # Calculate the range of allowable velocities after this frame
        lowerVel = max(
            -self.maxSpeed, self.velocity - self.acceleration * deltaT)
        upperVel = min(
            self.maxSpeed, self.velocity + self.acceleration * deltaT)

        # Calculate ideal velocity to come to rest based on v**2 = u**2 + 2as
        sTarget = target - self.value
        idealVel = copysign(
            (2. * self.acceleration * abs(sTarget)) ** 0.5,
            sTarget)

        self.velocity = max(lowerVel, min(upperVel, idealVel))
        self.value += self.velocity * deltaT

        return self.value


class ClockWatcher(Watcher):
    flashCycle = 0.5

    def start(self):
        self.lastVals = None

        self.text = self.app.fonts.timerFont.makeOnscreenText(
            self.app,
            align=TextNode.ACenter,
            parent=self.app.panda.a2dTopCenter,
            pos=(0, -0.08),
            text='',
        )
        self.task = self.app.panda.taskMgr.add(
            self.update, 'clockloop', priority=10)

    def stop(self):
        self.text.removeNode()
        if self.task:
            self.app.panda.taskMgr.remove(self.task)
            self.task = None

    def update(self, task):
        if not self.world.clock.showing:
            self.text.hide()
            return Task.cont

        self.text.show()
        text = self.world.clock.getTimeString()
        colours = self.app.theme.colours
        colour = colours.timerFontColour
        if self.world.clock.shouldFlash():
            if (self.world.clock.value // self.flashCycle) % 2:
                colour = colours.timerFlashColour

        if (text, colour) != self.lastVals:
            self.lastVals = (text, colour)
            self.text['text'] = text
            self.text['fg'] = colour

        return Task.cont


class RespawnNoticeWatcher(Watcher):

    def start(self):
        self.task = None
        self.localPlayer = None
        self.lastVals = None

        self.text = self.app.fonts.timerFont.makeOnscreenText(
            self.app,
            align=TextNode.ACenter,
            parent=self.app.panda.aspect2d,
            pos=(0, 0.12),
            text='',
        )
        self.activate()

    def activate(self, *args, **kwargs):
        if self.task is not None:
            return
        self.task = self.app.panda.taskMgr.add(
            self.update, 'respawnNoticeLoop', priority=10)
        self.text.show()

    def setLocalPlayer(self, player):
        if self.localPlayer is not None:
            self.localPlayer.onDied.removeListener(self.activate)
        self.localPlayer = player
        if player:
            player.onDied.addListener(self.activate)
            self.activate()

    def stop(self):
        self.setLocalPlayer(None)
        self.deactivate()
        self.text.removeNode()

    def deactivate(self):
        if self.task:
            self.app.panda.taskMgr.remove(self.task)
            self.text.hide()
            self.task = None

    def update(self, task):
        player = self.localPlayer
        if player is None or not player.dead:
            self.deactivate()
            return

        colours = self.app.theme.colours
        if not self.world.abilities.respawn:
            text = 'Please wait...'
            colour = colours.playerRespawnSoonText
        elif player.timeTillRespawn > 0:
            text = 'Respawn in {}...'.format(int(player.timeTillRespawn + 1))
            colour = colours.playerRespawnCountdownText
        elif not player.inRespawnableZone():
            text = 'Move to a friendly zone'
            colour = colours.playerRespawnSoonText
        elif player.getZone().frozen:
            text = 'This zone is frozen'
            colour = colours.playerRespawnSoonText
        else:
            text = 'Click to respawn'
            colour = colours.playerRespawnNowText

        if (text, colour) != self.lastVals:
            self.text['text'] = text
            self.text['fg'] = colour
        return Task.cont


class StatusBarOverlay(Watcher):
    def __init__(self, scene):
        super(StatusBarOverlay, self).__init__(scene)
        self.player = None
        self.needRefresh = True
        self.lastText = None
        self.lastCoinsText = None
        self.selectedUpgradeType = None

    def start(self):
        self.root = self.app.panda.a2dBottomCenter.attachNewNode('statusbar')
        self.root.setPos((0, 0, 0.15))

        self.panel = self.app.panda.loader.loadModel('statusbar.egg')
        texture = self.app.panda.loader.loadTexture('metal.png')
        self.panel.setTexture(texture)
        self.panel.setScale(0.1)
        self.panel.reparentTo(self.root)

        colours = self.app.theme.colours

        self.healthGauge = Gauge(
            app=self.app,
            parent=self.root,
            pos=(-0.35, 0, 0),
            width=0.7,
            height=0.08,
        )

        self.mainText = self.app.fonts.statusBarFont.makeOnscreenText(
            self.app,
            text='No player selected',
            align=TextNode.ACenter,
            parent=self.root,
            pos=(0, 0.03),
            fg=colours.playerStatusText,
        )

        self.coinGauge = Gauge(
            app=self.app,
            parent=self.root,
            pos=(0.25, 0, -0.08),
            width=0.1,
            height=0.08,
            vertical=True,
        )
        self.coinText = self.app.fonts.statusBarFont.makeOnscreenText(
            self.app,
            text='-',
            align=TextNode.ALeft,
            parent=self.root,
            pos=(0.29, -0.05),
            fg=colours.generalStatusText,
        )
        coin = makeCoin(self.app, scale=0.04)
        coin.reparentTo(self.root)
        coin.setPos((0.25, 0, -0.04))

        self.reloadGauge = Gauge(
            app=self.app,
            parent=self.root,
            pos=(-0.35, 0, -0.08),
            width=0.1,
            height=0.08,
            vertical=True,
        )
        gunBox = self.root.attachNewNode('')
        gun = self.app.theme.loadPandaImage('sprites', 'gun.png')
        gun.setTransparency(TransparencyAttrib.MAlpha)
        gun.reparentTo(gunBox)
        gunBox.setPos((-0.3, 0, -0.04))
        gunBox.setScale(2)

        self.task = self.app.panda.taskMgr.add(
            self.update, 'statusbarloop', priority=10)

    def setLocalPlayer(self, player):
        if self.player == player:
            return
        self.player = player
        self.needRefresh = True

    def update(self, task):
        if self.needRefresh:
            self.completeRefresh()
        self.updateText()
        if self.player:
            self.updateHealthGauge()
            self.updateReloadGauge()
            self.updateCoinGauge()

        return Task.cont

    def updateHealthGauge(self):
        if not self.player:
            self.healthGauge.setValue(0)
            return

        ratio = self.player.health / self.world.physics.playerRespawnHealth
        colours = self.app.theme.colours
        if self.world.physics.playerRespawnHealth == 1:
            colour = colours.goodHealth
        elif ratio <= 0.25 or self.player.health == 1:
            colour = colours.badHealth
        elif ratio <= 0.55:
            colour = colours.fairHealth
        else:
            colour = colours.goodHealth
        self.healthGauge.setValue(ratio, colour=colour)

    def updateReloadGauge(self):
        player = self.player
        if not player:
            self.reloadGauge.setValue(0)
            return

        colours = self.app.theme.colours
        if player.machineGunner and player.mgBulletsRemaining > 0:
            ratio = player.mgBulletsRemaining / 15.
            colour = colours.gaugeGood
        elif player.reloadTime > 0:
            ratio = 1 - player.reloadTime / (player.reloadFrom + 0.)
            colour = colours.gaugeBad
        else:
            ratio = 1
            colour = colours.gaugeGood

        self.reloadGauge.setValue(ratio, colour=colour)

    def updateCoinGauge(self):
        if not self.player or not self.selectedUpgradeType:
            self.coinGauge.setValue(0)
            return

        colours = self.app.theme.colours
        required = self.selectedUpgradeType.requiredCoins
        if required == 0:
            ratio = 1
            colour = colours.gaugeGood
        else:
            ratio = self.player.coins / required
            if ratio < 1:
                colour = colours.gaugeBad
            else:
                colour = colours.gaugeGood
        self.coinGauge.setValue(ratio, colour=colour)

    def completeRefresh(self):
        self.needRefresh = False
        if not self.player:
            self.updateHealthGauge()
            self.updateReloadGauge()
            self.updateCoinGauge()

    def updateText(self):
        if not self.player:
            text = 'No player selected'
        else:
            text = self.player.nick

        if text != self.lastText:
            self.mainText['text'] = self.lastText = text

        if not self.player:
            coinText = '-'
        else:
            coinText = str(self.player.coins)
        if coinText != self.lastCoinsText:
            self.coinText['text'] = self.lastCoinsText = coinText

    def stop(self):
        self.root.removeNode()
        if self.task:
            self.app.panda.taskMgr.remove(self.task)
            self.task = None


class Gauge(object):
    def __init__(
            self, app, parent, pos, width, height, colour=None,
            vertical=False, alpha=0.3):
        self.frame = parent.attachNewNode('')
        self.box = box = app.panda.loader.loadModel('box.egg')
        box.setSy(0.01)
        if vertical:
            box.setHpr((0, 0, 90))
            self.frame.setSx(width)
            self.frame.setSz(-height)
        else:
            self.frame.setSx(width)
            self.frame.setSz(height)

        if alpha < 1:
            box.setTransparency(TransparencyAttrib.MAlpha)
            box.setAlphaScale(alpha)
        if colour is not None:
            box.setColor(colour)

        self.frame.setPos(pos)
        self.box.setSx(0)
        box.reparentTo(self.frame)

    def setValue(self, value, colour=None):
        if colour:
            self.box.setColor(colour)
        self.box.setSx(max(0, min(1, value)))


class MiniMapDisplay(Watcher):
    def __init__(self, scene):
        super(MiniMapDisplay, self).__init__(scene)

        self.camera = Camera('miniMapCam')
        self.camera.setCameraMask(MINIMAP_ONLY)
        self.cameraNP = NodePath(self.camera)
        self.region = None
        self.do = DirectObject()

    def start(self):
        if self.region is None:
            self.region = self.app.panda.win.makeDisplayRegion(0.7, 1, 0.85, 1)
            self.region.setCamera(self.cameraNP)
            self.region.setSort(5)
            self.region.setClearDepthActive(True)
            self.camera.getLens().setFov(53.13)

        self.cameraNP.reparentTo(self.scene.miniMapCamera)
        self.cameraNP.setPos((0, 0, 0))
        self.region.setActive(True)
        self.do.accept('aspectRatioChanged', self.aspectRatioChanged)
        self.aspectRatioChanged()

    def stop(self):
        if self.region:
            self.region.setActive(False)
        self.cameraNP.removeNode()
        self.do.ignoreAll()

    def aspectRatioChanged(self):
        # The aspect ratio of the minimap is 2 * the aspect ratio of the game
        aspectRatio = self.app.panda.getAspectRatio()
        self.camera.getLens().setAspectRatio(2 * aspectRatio)


class SingleZoneWatcher(Watcher):
    def __init__(self, scene, zone):
        super(SingleZoneWatcher, self).__init__(scene)
        self.zone = zone
        self.background = None
        self.miniBackground = None
        self.orb = None
        self.sparkles = []
        self.orbSpin = None

        light = AmbientLight('zoneAmbientLight')
        light.setColor((.2, .2, .2, 1))
        self.ambientLight = self.scene.reparent(NodePath(light))

    def start(self):
        self.topNode = self.app.panda.render.attachNewNode('zone')
        self.topNode.setPos(mapPosToPanda(self.zone.defn.pos))

        self.background = self.makeZoneBackground()
        self.background.reparentTo(self.topNode)
        self.miniBackground = self.makeMiniMapBackground()
        self.miniBackground.reparentTo(self.topNode)

        self.orb, self.orbSpin = self.makeOrb()
        self.orb.reparentTo(self.topNode)

        self.updateZoneOwnership()

    def stop(self):
        self.background.removeNode()
        self.orb.removeNode()
        while self.sparkles:
            self.sparkles.pop(0).cleanup()

    def makeOrb(self):
        orb = self.app.panda.loader.loadModel('orb.egg')
        orb.setTexture(self.app.panda.loader.loadTexture('smoke.jpg'))
        orb.setPos((0, 2, 0))
        orb.clearLight()
        orb.setLight(self.scene.fullAmbientLight)
        orb.hide(BitMask32.allOn())
        orb.show(MAIN_VIEW_ONLY)

        spin = Sequence(
            orb.hprInterval(1.0, (400, 0, 0)),
            orb.hprInterval(1.0, (600, 200, 0)),
            orb.hprInterval(1.0, (600, 600, 0)),
            orb.hprInterval(1.0, (400, 1000, 0)),
            orb.hprInterval(1.0, (0, 1200, 0)),
            orb.hprInterval(1.0, (-400, 1200, 0)),
            orb.hprInterval(1.0, (-600, 1000, 0)),
            orb.hprInterval(1.0, (-600, 600, 0)),
            orb.hprInterval(1.0, (-400, 200, 0)),
            orb.hprInterval(1.0, (0, 0, 0)),
        )
        spin.loop()
        spin.pause()

        return orb, spin

    def makeZoneBackground(self):
        loader = self.app.panda.loader
        room = loader.loadModel('room.egg')

        def setMaterial(groupName, material):
            g = room.find('**/' + groupName)
            texture = loader.loadTexture(material + '_albedo.jpg')
            g.setTexture(texture)
            texture = loader.loadTexture(material + '_normal.jpg')
            g.setTexture(self.scene.normals, texture)
            texture = loader.loadTexture(material + '_metallic.jpg')
            g.setTexture(self.scene.gloss, texture)
        setMaterial('SciFi_GameBK03:TopGroup', 'SciFi_GameBK03_Tops')
        setMaterial('SciFi_GameBK03:EstructureGroup', 'SciFi_GameBK03_Structure')
        setMaterial('SciFi_GameBK03:TubesGroup', 'SciFi_GameBK03_Tubes')
        setMaterial('SciFi_GameBK03:Panels', 'SciFi_GameBK03_Panel')

        light = PointLight('light')
        light.setAttenuation((0.5, 0, 0))
        NodePath(light).reparentTo(room.find('**/Lamp'))

        room.setPos(0, 0, -24)
        room.setLight(room.find('**/light'))
        room.setLight(self.scene.cameraSpotLight)
        room.setLight(self.ambientLight)

        room.hide(BitMask32.allOn())
        room.show(MAIN_VIEW_ONLY)

        return room

    def makeMiniMapBackground(self):
        loader = self.app.panda.loader
        shape = loader.loadModel('zonehex.egg')

        shape.setLight(self.ambientLight)
        shape.setPos(0, 2, 0)

        shape.hide(BitMask32.allOn())
        shape.show(MINIMAP_ONLY)

        return shape

    def stateChanged(self):
        self.updateZoneOwnership()

    def updateZoneOwnership(self):
        colour = self.app.theme.colours.getTeamColour(
            self.zone.owner, 'OrbTint')
        self.orb.setColorScale(colour)
        self.miniBackground.setColorScale(colour)

        self.updateRoomOwnership()
        self.updateSparkle()
        if self.zone.owner:
            self.orbSpin.resume()
        else:
            self.orbSpin.pause()

    def updateRoomOwnership(self):
        room = self.background
        lightNode = room.find('**/light').node()
        colour = self.app.theme.colours.getTeamColour(self.zone.owner, 'Zone')
        lightNode.setColor(colour)

        if self.zone.dark:
            specular = self.app.theme.colours.getTeamColour(
                self.zone.owner, 'Specular')
            lightNode.setSpecularColor(specular)
            ambient = self.app.theme.colours.getTeamColour(
                self.zone.owner, 'Ambient')
        else:
            lightNode.setSpecularColor((0, 0, 0, 1))
            ambient = self.app.theme.colours.getTeamColour(None, 'Ambient')

        self.ambientLight.node().setColor(ambient)

    def updateSparkle(self):
        while self.sparkles:
            self.sparkles.pop(0).cleanup()

        if self.zone.owner:
            if self.app.displaySettings.orbSparkles:
                sparkleColours = ('OrbSparkle1', 'OrbSparkle2')
            else:
                sparkleColours = ()

            for colourName in sparkleColours:
                sparkle = ParticleEffect()
                sparkle.loadConfig(getPandaPath('config/sparkle.ptf'))
                sparkle.setPos((0, 2, 0))
                particles = sparkle.particlesDict['particles-1']
                colour = self.app.theme.colours.getTeamColour(
                    self.zone.owner, colourName)
                particles.renderer.setCenterColor(colour)
                particles.renderer.setEdgeColor(colour)
                self.sparkles.append(sparkle)

                sparkle.start(parent=self.topNode)
                sparkle.hide(BitMask32.allOn())
                sparkle.show(MAIN_VIEW_ONLY)

                sparkle.clearLight()
                sparkle.setLight(self.scene.fullAmbientLight)


class ZoneWatcher(Watcher):
    '''
    Makes sure that all the zone ownership sprites are kept up to date.
    '''

    def __init__(self, scene):
        super(ZoneWatcher, self).__init__(scene)

        self.zoneWatchers = {}

    def start(self):
        self.world.onZoneStateChanged.addListener(self.zoneStateChanged)
        self.world.onReset.addListener(self.worldReset)
        self.createZones()

    def createZones(self):
        for zone in self.world.zones:
            watcher = SingleZoneWatcher(self.scene, zone)
            self.zoneWatchers[zone.id] = watcher
            watcher.start()

    def stop(self):
        self.world.onZoneStateChanged.removeListener(self.zoneStateChanged)
        self.world.onReset.removeListener(self.worldReset)
        self.cleanUp()

    def cleanUp(self):
        for zoneId in list(self.zoneWatchers):
            self.zoneWatchers.pop(zoneId).stop()

    def worldReset(self):
        self.cleanUp()
        self.createZones()

    def zoneStateChanged(self, zone):
        self.zoneWatchers[zone.id].stateChanged()


class AllCoinsWatcher(Watcher):
    def __init__(self, scene):
        super(AllCoinsWatcher, self).__init__(scene)
        self.coins = {}

    def start(self):
        for coin in list(self.world.collectableCoins.values()):
            self.newCoin(coin)

        self.world.onCollectableCoinSpawned.addListener(self.newCoin)
        self.world.onCoinSound.addListener(self.gotCoin)

    def stop(self):
        self.world.onCollectableCoinSpawned.removeListener(self.newCoin)
        self.world.onCoinSound.removeListener(self.gotCoin)

        for coin in list(self.coins.keys()):
            self.coinGone(coin)

    def newCoin(self, coin):
        coin.onVanish.addListener(self.coinGone)
        watcher = SingleCoinWatcher(self.scene, coin)
        self.coins[coin] = watcher
        watcher.start()

    def coinGone(self, coin):
        watcher = self.coins.pop(coin)
        watcher.stop()
        coin.onVanish.removeListener(self.coinGone)

    def gotCoin(self, player):
        if (
                self.scene.localState.player
                and player.id == self.scene.localState.player.id):
            self.app.soundPlayer.play('gotCoin', 1.5)
        else:
            self.scene.playDistanceSound('gotCoin', player.pos)


def makeCoin(app, scale=1.0):
    coinNode = app.panda.loader.loadModel('coin.egg')
    coinNode.setScale(0.7 * scale)
    texture = app.panda.loader.loadTexture('coin.png')
    coinNode.setTexture(texture)
    return coinNode


class SingleCoinWatcher(Watcher):
    INITIAL_ROTATION = 1000
    TERMINAL_ROTATION = 120
    ROTATION_DROPOFF = 0.75

    def __init__(self, scene, coin):
        super(SingleCoinWatcher, self).__init__(scene)
        self.coin = coin
        name = 'coin{}'.format(coin.id)
        self.tracer = self.app.panda.render.attachNewNode(name)
        self.coinNode = None
        self.task = None
        self.heading = 0
        self.lastTime = 0
        self.rotationSpeed = self.INITIAL_ROTATION

    def start(self):
        self.coinNode = coinNode = makeCoin(self.app)
        coinNode.reparentTo(self.tracer)
        coinNode.setHpr((self.heading, 0, 0))

        self.task = self.app.panda.taskMgr.add(
            self.update, 'coin{}loop'.format(self.coin.id), priority=10)
        self.lastTime = self.task.time

    def stop(self):
        self.tracer.removeNode()
        if self.task:
            self.app.panda.taskMgr.remove(self.task)
            self.task = None

    def update(self, task):
        if self.coin.hitLocalPlayer:
            self.stop()
            return

        pos = self.coin.tweenPos(self.scene.tweenFraction)
        self.tracer.setPos(mapPosToPanda(pos))

        deltaT = task.time - self.lastTime
        self.lastTime += deltaT
        self.heading = (self.heading + self.rotationSpeed * deltaT) % 360
        self.rotationSpeed = max(
            self.TERMINAL_ROTATION,
            self.rotationSpeed * (self.ROTATION_DROPOFF ** deltaT),
        )
        self.coinNode.setHpr((self.heading, 0, 0))

        tick = self.world.getMonotonicTick()
        fadeTick = self.coin.creationTick + (
            COLLECTABLE_COIN_LIFETIME - 2) // TICK_PERIOD
        if tick >= fadeTick:
            alpha = random.random() * .625 + .125
            self.coinNode.setTransparency(TransparencyAttrib.MAlpha)
            self.coinNode.setAlphaScale(alpha)

        return Task.cont


class AllPlayersAndShotsWatcher(Watcher):
    '''
    Keeps player state up to date for all players.
    '''

    def __init__(self, scene):
        super(AllPlayersAndShotsWatcher, self).__init__(scene)

        self.players = {}
        self.shots = {}
        self.localShots = {}

    def start(self):
        for player in self.world.players:
            self.playerAdded(player)

        self.world.onPlayerAdded.addListener(self.playerAdded)
        self.world.onPlayerRemoved.addListener(self.playerRemoved)
        self.world.onShotRemoved.addListener(self.shotRemoved)
        self.scene.localState.onAddLocalShot.addListener(self.localShotAdded)
        self.scene.localState.onRemoveLocalShot.addListener(
            self.localShotRemoved)

    def stop(self):
        self.world.onPlayerAdded.removeListener(self.playerAdded)
        self.world.onPlayerRemoved.removeListener(self.playerRemoved)
        self.world.onShotRemoved.removeListener(self.shotRemoved)
        self.scene.localState.onAddLocalShot.removeListener(
            self.localShotAdded)
        self.scene.localState.onRemoveLocalShot.removeListener(
            self.localShotRemoved)

        for playerId in list(self.players.keys()):
            self.stopPlayerWatcher(playerId)
        for shotId in list(self.shots.keys()):
            self.stopShotWatcher(shotId)
        for shot in list(self.localShots.keys()):
            self.stopLocalShotWatcher(shot)

    def setLocalPlayer(self, player):
        if player.id in self.players:
            self.stopPlayerWatcher(player.id)
        self.playerAdded(player, local=True)

    def playerAdded(self, player, local=False):
        watcher = SinglePlayerWatcher(self.scene, player, local=local)
        self.players[player.id] = watcher
        watcher.start()
        if not local:
            player.onShotFired.addListener(self.shotFired)

    def playerRemoved(self, player, oldId):
        self.stopPlayerWatcher(oldId)

    def stopPlayerWatcher(self, playerId):
        watcher = self.players.pop(playerId)
        watcher.stop()
        watcher.player.onShotFired.removeListener(self.shotFired)

    def shotRemoved(self, shotId):
        self.stopShotWatcher(shotId, sparks=True)

    def stopShotWatcher(self, shotId, sparks=False):
        if shotId not in self.shots:
            # e.g. the real shot for a local player
            return
        watcher = self.shots.pop(shotId)
        if sparks:
            watcher.sparks()
        watcher.stop()

    def shotFired(self, shot):
        watcher = SingleShotWatcher(self.scene, shot)
        self.shots[shot.id] = watcher
        watcher.start()

    def localShotAdded(self, shot):
        watcher = SingleShotWatcher(self.scene, shot)
        self.localShots[shot] = watcher
        watcher.start()

    def localShotRemoved(self, shot):
        # Introduce a delay so that the local shot doesn't suddenly vanish
        reactor.callLater(0.02, self.stopLocalShotWatcher, shot)

    def stopLocalShotWatcher(self, shot):
        if shot not in self.localShots:
            # Because of the delay, we might have shut down before this call
            return
        watcher = self.localShots.pop(shot)
        watcher.sparks()
        watcher.stop()


class PlayerInputResponder(DirectObject):
    NO_GHOST_THRUST_MOUSE_RADIUS = 1.5      # metres
    FULL_GHOST_THRUST_MOUSE_RADIUS = 7.5    # metres

    def __init__(self, scene, player):
        self.scene = scene
        self.app = self.scene.app
        self.player = player
        self.task = None
        self.shooting = False

    def sendRequest(self, msg):
        self.scene.gameInterface.sendRequest(msg)

    def getTickId(self):
        return self.player.world.lastTickId

    def start(self):
        self.task = self.app.panda.taskMgr.add(
            self.update, 'player{}inputLoop'.format(
                ord(self.player.id)), priority=10)

        self.accept('mouse1', self.leftMouseClicked)
        self.accept('mouse1-up', self.leftMouseReleased)
        self.accept('mouse3', self.rightMouseClicked)
        self.accept('mouse3-up', self.rightMouseReleased)

        self.accept(
            keyDownEvent(ACTION_LEFT), self.keyStateChange, [LEFT_STATE, True])
        self.accept(
            keyUpEvent(ACTION_LEFT), self.keyStateChange, [LEFT_STATE, False])
        self.accept(
            keyDownEvent(ACTION_RIGHT), self.keyStateChange, [RIGHT_STATE, True])
        self.accept(
            keyUpEvent(ACTION_RIGHT), self.keyStateChange, [RIGHT_STATE, False])
        self.accept(
            keyDownEvent(ACTION_JUMP), self.keyStateChange, [JUMP_STATE, True])
        self.accept(
            keyUpEvent(ACTION_JUMP), self.keyStateChange, [JUMP_STATE, False])
        self.accept(
            keyDownEvent(ACTION_DOWN), self.keyStateChange, [DOWN_STATE, True])
        self.accept(
            keyUpEvent(ACTION_DOWN), self.keyStateChange, [DOWN_STATE, False])

        self.accept(keyDownEvent(ACTION_RESPAWN), self.doRespawn)
        self.accept(keyDownEvent(ACTION_EMOTE), self.doEmote)
        self.accept(keyDownEvent(ACTION_READY), self.toggleReady)
        self.accept(keyDownEvent(ACTION_PAUSE_GAME), self.pauseGame)

    def doRespawn(self):
        self.sendRequest(RespawnRequestMsg(tickId=self.getTickId()))

    def doEmote(self):
        self.sendRequest(
            EmoteRequestMsg(
                tickId=self.getTickId(),
                emoteId=random.randrange(MAX_EMOTE + 1)))

    def toggleReady(self):
        if self.player.readyToStart:
            self.sendRequest(PlayerIsReadyMsg(self.player.id, False))
        else:
            self.sendRequest(PlayerIsReadyMsg(self.player.id, True))

    def pauseGame(self):
        world = self.player.world
        if world.isServer:
            world.pauseOrResumeGame()
            if world.paused:
                self.newMessage('Game paused')
            else:
                self.newMessage('Game resumed')
        else:
            self.newMessage(
                'You can only pause games from the server', error=True)

    def newMessage(self, msg, error=False):
        # TODO: port to Panda, and other uses of newMessage()
        log.error('newMessage() not yet ported to panda!')

    def stop(self):
        self.app.panda.taskMgr.remove(self.task)
        self.ignoreAll()

    def update(self, task):
        target = self.scene.getMouseTarget()
        if target is not None:
            self.updateMouseAngle(target)

        if self.shooting and self.player.canShoot():
            self.fireOneShot()

        return Task.cont

    def updateMouseAngle(self, target):
        pos = self.player.tweenPos(self.scene.tweenFraction)
        diff = target - mapPosToPanda(pos)
        theta = atan2(diff.getX(), diff.getZ())
        dist = diff.length()

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

        lastTickId = self.getTickId()
        self.sendRequest(AimPlayerAtMsg(theta, thrust, tickId=lastTickId))

    def leftMouseClicked(self):
        if self.player.dead:
            self.sendRequest(RespawnRequestMsg(tickId=self.getTickId()))
        else:
            self.shooting = True
            self.fireOneShot()

    def fireOneShot(self):
        self.sendRequest(ShootMsg(self.getTickId()))

    def leftMouseReleased(self):
        self.shooting = False

    def rightMouseClicked(self):
        # TODO: enable grenade trajectory
        pass

    def rightMouseReleased(self):
        # TODO: disable grenade trajectory
        pass

    def keyStateChange(self, key, value):
        self.sendRequest(UpdatePlayerStateMsg(
            value, stateKey=key, tickId=self.getTickId()))


class LivePlayerModel(object):
    def __init__(self, parent, team):
        self.currentAngleFrame = 0
        self.currentHeading = 0
        self.currentLegAnim = None
        self.aimFPS = 240

        self.actor = Actor('player', {
            'run': 'player-run',
            'walk': 'player-walk',
            'aim': 'player-aim',
            'stand': 'player-stand',
        })
        self.actor.makeSubpart('legs', ['Body'], ['Spine1'])
        self.actor.makeSubpart('torso', ['Spine1'])
        self.actor.setMaterial(getPlayerMaterial(team))

        self.actor.setScale(0.5)
        ignore, yOffset = mapSizeToPanda((0, Player.HALF_HEIGHT - 5))
        self.actor.setPos((0, 0, -yOffset))
        self.actor.hide(BitMask32.allOn())

        # Find the frame rate and frame count of the aiming animation
        controls = self.actor.getAnimControls('aim', partName='torso')
        self.aimFPS = controls[0].getFrameRate() * 4
        self.aimFrames = controls[0].getNumFrames() - 1

        self.actor.reparentTo(parent)

    def cleanup(self):
        self.actor.cleanup()

    def setTeam(self, team):
        self.actor.setMaterial(getPlayerMaterial(team))

    def hide(self):
        self.actor.hide(BitMask32.allOn())

    def show(self):
        self.actor.show(MAIN_VIEW_ONLY)

    def updateAim(self, deltaT, targetAngle, reset=False):
        targetFrame = int(
            abs(targetAngle) * self.aimFrames / pi + 0.5)
        if targetAngle > 0:
            targetHeading = 90
        else:
            targetHeading = -90

        if reset:
            self.currentAngleFrame = targetFrame
            self.currentHeading = targetHeading
            self.currentLegAnim = None
        else:
            self.currentAngleFrame = self.moveTowards(
                self.currentAngleFrame, targetFrame, deltaT * self.aimFPS)
            degreesPerSecond = 1200
            self.currentHeading = self.moveTowards(
                self.currentHeading, targetHeading, deltaT * degreesPerSecond)

        self.actor.setHpr(self.currentHeading, 0, 0)
        self.actor.pose('aim', self.currentAngleFrame, partName='torso')

    def updateLegs(self, deltaT, isOnGround, xVel, yVel):
        if isOnGround:
            if not xVel:
                anim = 'stand'
                loop = False
            elif self.currentHeading * xVel > 0:
                anim = 'run'
                loop = True
            else:
                anim = 'walk'
                loop = True
        else:
            # TODO: actually design the jump and fall animations
            if yVel > 0:
                anim = 'jump'
                loop = False
            else:
                anim = 'fall'
                loop = False

        if self.currentLegAnim != anim:
            self.actor.stop(partName='legs')
            self.currentLegAnim = anim
            if loop:
                self.actor.loop(anim, partName='legs')
            else:
                self.actor.play(anim, partName='legs')

    def moveTowards(self, value, target, amount):
        if target < value:
            return max(value - amount, target)
        return min(value + amount, target)



class SinglePlayerWatcher(Watcher):
    def __init__(self, scene, player, local=False):
        super(SinglePlayerWatcher, self).__init__(scene)
        self.player = player
        self.task = None
        self.resetPlayer = True
        self.lastTime = 0

        self.inputResponder = None
        if local:
            self.inputResponder = PlayerInputResponder(scene, player)

    def start(self):
        self.player.onTeamSet.addListener(self.teamChanged)

        self.nodePath = NodePath('player')
        self.liveModel = LivePlayerModel(self.nodePath, self.player.team)
        self.liveModel.actor.setLight(self.scene.lowAmbientLight)
        self.liveModel.actor.setLight(self.scene.cameraSpotLight)

        self.ghostImage = OnscreenImage(
            self.app.theme.sprites.ghostTexture(self.player.team),
            scale=(1.28, 1, 1.53))
        self.ghostImage.setTransparency(TransparencyAttrib.MAlpha)
        self.ghostImage.setPos((0, -1, 0))
        self.ghostImage.setAlphaScale(0.35)
        self.ghostImage.hide(BitMask32.allOn())
        self.ghostImage.setLight(self.scene.fullAmbientLight)

        colours = self.app.theme.colours
        self.minimapPoint = self.app.panda.loader.loadModel('sphere.egg')
        self.minimapPoint.setColor(colours.miniMapColour(self.player.team))
        self.minimapPoint.setScale(2)
        self.minimapPoint.hide(BitMask32.allOn())
        self.minimapPoint.show(MINIMAP_ONLY)

        self.nodePath.reparentTo(self.app.panda.render)
        self.ghostImage.reparentTo(self.nodePath)
        self.minimapPoint.reparentTo(self.nodePath)

        self.task = self.app.panda.taskMgr.add(
            self.update, 'player{}loop'.format(
                ord(self.player.id)), priority=10)
        self.lastTime = self.task.time

        if self.inputResponder:
            self.inputResponder.start()

    def stop(self):
        self.player.onTeamSet.removeListener(self.teamChanged)
        self.liveModel.cleanup()
        self.app.panda.taskMgr.remove(self.task)
        self.nodePath.removeNode()
        if self.inputResponder:
            self.inputResponder.stop()

    def teamChanged(self):
        self.liveModel.setTeam(self.player.team)
        self.ghostImage.setTexture(
            self.app.theme.sprites.ghostTexture(self.player.team))
        self.minimapPoint.setColor(
            self.app.theme.colours.miniMapColour(self.player.team))

    def update(self, task):
        deltaT = task.time - self.lastTime
        self.lastTime = task.time
        pos = self.player.tweenPos(self.scene.tweenFraction)
        pos = (pos[0], pos[1] + 6)      # TODO: remove artificial offset
        self.nodePath.setPos(mapPosToPanda(pos))

        if self.player.dead:
            self.updateGhost(deltaT)
        else:
            self.updateLivePlayer(deltaT)

        return Task.cont

    def updateGhost(self, deltaT):
        self.liveModel.hide()
        self.ghostImage.show(MAIN_VIEW_ONLY)
        self.resetPlayer = True
        self.minimapPoint.setScale(1.5)

        if self.player._faceRight:
            self.ghostImage.setTexOffset(TextureStage.getDefault(), 0, 0)
            self.ghostImage.setTexScale(TextureStage.getDefault(), 1, 1)
        else:
            self.ghostImage.setTexOffset(TextureStage.getDefault(), 1, 0)
            self.ghostImage.setTexScale(TextureStage.getDefault(), -1, 1)

    def updateLivePlayer(self, deltaT):
        self.ghostImage.hide(BitMask32.allOn())
        self.liveModel.show()
        self.minimapPoint.setScale(2.5)

        # TODO: special case for holding on to wall, set whole body animation
        self.liveModel.updateAim(
            deltaT, self.player.angleFacing, self.resetPlayer)
        self.liveModel.updateLegs(deltaT, self.player.isOnGround(),
            (self.player.pos[0] - self.player.oldPos[0]) / deltaT,
            self.player.yVel)
        self.resetPlayer = False


class SingleShotWatcher(Watcher):
    def __init__(self, scene, shot):
        super(SingleShotWatcher, self).__init__(scene)
        self.shot = shot
        name = 'shot{}'.format(shot.id)
        self.tracer = self.app.panda.render.attachNewNode(name)
        self.task = None
        self.showing = False
        self.mainViewSphere = None
        self.miniMapSphere = None

    def start(self):
        sphere = self.app.panda.loader.loadModel('sphere.egg')
        self.mainViewSphere = sphere
        sphere.setMaterial(getShotMaterial(self.shot.team))
        sphere.hide(BitMask32.allOn())
        sphere.reparentTo(self.tracer)
        sphere.setLight(self.scene.fullAmbientLight)

        sphere = self.app.panda.loader.loadModel('sphere.egg')
        self.miniMapSphere = sphere
        sphere.setScale(1.4)
        sphere.setMaterial(getMiniMapShotMaterial(self.shot.team))
        sphere.hide(BitMask32.allOn())
        sphere.reparentTo(self.tracer)
        sphere.setLight(self.scene.fullAmbientLight)

        self.task = self.app.panda.taskMgr.add(
            self.update, 'shot{}loop'.format(self.shot.id), priority=10)

    def stop(self):
        self.tracer.removeNode()
        if self.task:
            self.app.panda.taskMgr.remove(self.task)

    def update(self, task):
        if not self.showing and not self.shot.justFired:
            self.showing = True
            self.mainViewSphere.show(MAIN_VIEW_ONLY)
            self.miniMapSphere.show(MINIMAP_ONLY)

        angle = atan2(self.shot.vel[1], self.shot.vel[0])
        self.mainViewSphere.setR(angle * 180 / pi)

        pos = mapPosToPanda(self.shot.tweenPos(self.scene.tweenFraction))
        self.tracer.setPos(pos)

        # TODO: use information in futureBounces
        # contactPoint = mapPosToPanda(self.shot.contactPoint)
        # length = max(0.1, min(1, 2 * distance(contactPoint, pos)))
        length = 1
        self.mainViewSphere.setScale((length, 0.15, 0.15))

        return Task.cont

    def sparks(self):
        sparks = ParticleEffect()
        sparks.loadConfig(getPandaPath('config/sparks.ptf'))

        particles = sparks.particlesDict['particles-1']
        particles.setBirthRate(10)

        x, z = mapSizeToPanda(self.shot.vel)
        particles.emitter.setOffsetForce((0.3 * x, 0, 0.3 * z))
        particles.induceLabor()

        node = self.app.panda.render.attachNewNode('sparks')
        node.setPos(mapPosToPanda(self.shot.pos))
        sparks.start(parent=node)
        sparks.clearLight()
        sparks.setLight(self.scene.fullAmbientLight)

        def removeSparks(task):
            sparks.cleanup()
            node.removeNode()

        self.app.panda.taskMgr.doMethodLater(0.5, removeSparks,
            'removeSparks')