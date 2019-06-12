# coding: utf-8
import codecs
import logging
import os
import time
from tkinter import Tk
from math import pi
from tkinter.filedialog import askopenfilename
from twisted.internet import defer, task, tksupport

from direct.gui.DirectGui import (
    DirectButton, DGG, DirectScrolledList, DirectLabel, YesNoDialog,
    OkCancelDialog, DirectRadioButton, DirectEntry, OkDialog, DirectFrame,
    DirectCheckButton)
from direct.gui.OnscreenText import TextNode
from direct.showbase.DirectObject import DirectObject
from direct.task import Task
from panda3d.core import (
    PointLight, AmbientLight, Spotlight, PerspectiveLens, Mat4, NodePath,
    TransparencyAttrib, Camera, OrthographicLens,
)

import trosnoth.version
from trosnoth import const
from trosnoth.client3d.base.app import PandaScene
from trosnoth.client3d.ingame.gameInterface import (
    LivePlayerModel, MAIN_VIEW_ONLY,
)
from trosnoth.client3d.pregame.playscreen import PlayConnector
from trosnoth.client3d.pregame.savedGameMenu import Archivist
from trosnoth.client3d.settings.settings import SettingsScreen
from trosnoth.data import getPath, startupMenu, user
from trosnoth.game import LocalGame
from trosnoth.gamerecording.gamerecorder import replayDir
from trosnoth.gamerecording.replays import ReplayFileError
from trosnoth.utils.gui import align

log = logging.getLogger(__name__)

CREDITS_SCROLL_SPEED = 0.25
MAX_LOG_ITEMS = 16

# For debugging the position of the camera in the title menu
TITLE_MENU_ENABLE_PANNING = True


class TeamA(object):
    '''
    Used for dummy player on front screen, to determine colours etc.
    '''
    id = b'A'


class StartupScene(PandaScene):
    tweenFraction = 0

    def __init__(self, *args, **kwargs):
        super(StartupScene, self).__init__(*args, **kwargs)
        self.joinScreen = JoinScreenHelper(self.app, self)
        self.settingsScreen = SettingsScreen(self.app, self,
                                             self.showMainMenu)
        self.archivesScreen = ArchivesScreenHelper(self.app, self)
        self.serversScreen = ServersScreenHelper(self.app, self)
        self.playerModel = None
        self.title = None
        self.creditsReel = None

        self.visibleNode = None
        self.mainMenuNode = None
        self.creditsNode = None
        self.archivesNode = None
        self.settingsNode = None
        self.joinNode = None

    def start(self):
        self.setupScene()
        self.setupCamera()
        self.setupLights()
        self.setupMainMenu()
        self.setupCredits()
        self.setupSettings()
        self.setupArchives()
        self.setupServers()
        self.setupJoin()

        if __debug__ and TITLE_MENU_ENABLE_PANNING:
            task.LoopingCall(self.logCameraDetails).start(5)

    def logCameraDetails(self):
        log.error(
            'camera: %r %r', self.app.panda.camera.getPos(),
            self.app.panda.camera.getHpr())

    def stop(self):
        if self.playerModel:
            self.playerModel.cleanup()
        self.creditsReel.stop()
        self.joinScreen.stop()
        if __debug__ and TITLE_MENU_ENABLE_PANNING:
            self.app.panda.disableMouse()
        super(StartupScene, self).stop()

    def showOkDialog(self, text):
        d = defer.Deferred()
        def ok(result):
            dialog.cleanup()
            d.callback(None)

        dialog = OkDialog(
            dialogName='replayError',
            text=text,
            command=ok,
            fadeScreen=0.3,
            button_pad=(0.1, 0.03),
            buttonPadSF=1.3,
        )
        dialog.show()
        return d

    def showNode(self, node):
        self.creditsReel.stop()
        self.joinScreen.stop()
        if self.visibleNode is not None:
            self.visibleNode.hide()
        self.visibleNode = node
        node.show()

    def showMainMenu(self):
        self.showNode(self.mainMenuNode)

    def showCredits(self):
        self.showNode(self.creditsNode)
        self.creditsReel.start()

    def showSettings(self):
        self.showNode(self.settingsNode)
        self.settingsScreen.show()

    def showArchives(self):
        self.showNode(self.archivesNode)
        self.archivesScreen.show()

    def showServers(self):
        self.showNode(self.serversNode)
        self.serversScreen.show()

    def showJoin(self, servers=None):
        self.showNode(self.joinNode)
        self.joinScreen.show(servers)

    def setupScene(self):
        scene = self.app.panda.loader.loadModel('titlemenu.egg')
        self.reparent(scene, self.app.panda.render)

        if self.playerModel is None:
            self.playerModel = LivePlayerModel(self.app.panda.render, TeamA())
            self.playerModel.updateAim(0.1, -0.5 * pi, reset=True)
            self.playerModel.updateLegs(0.1, True, 0, 0)
            self.playerModel.actor.setPos((0, 0, 1.6))
            self.playerModel.show()

        self.title = self.app.theme.loadPandaImage(
            'startupMenu', 'title.png')
        self.title.setZ(0.75 - self.title.getSz())
        self.reparent(self.title, self.app.panda.plaque)

        vFont = self.app.screenManager.fonts.versionFont
        versionText = vFont.makeOnscreenText(
            self.app,
            text=trosnoth.version.titleVersion,
            fg=self.app.theme.colours.versionColour,
            align=TextNode.ARight,
            pos=(-0.02, 0.02),
        )
        self.reparent(versionText, self.app.panda.a2dBottomRight)

    def setupCamera(self):
        self.app.panda.cam.node().setCameraMask(MAIN_VIEW_ONLY)

        camera = self.app.panda.camera
        camera.setPos((-5, -7.5, 2.5))
        camera.lookAt((0, 5, 0.5))

        if __debug__ and TITLE_MENU_ENABLE_PANNING:
            mat = Mat4(camera.getMat())
            mat.invertInPlace()
            self.app.panda.mouseInterfaceNode.setMat(mat)
            self.app.panda.enableMouse()

    def setupLights(self):
        panda = self.app.panda

        panda.setBackgroundColor(.9, .9, .9, 1)
        panda.render.clearLight()

        keylight = Spotlight('keylight')
        keylight.setLens(PerspectiveLens())
        np = self._insertLight(
            keylight,
            colour=(1, 1, 1, 1),
            pos=(0, -5, 2),
        )
        np.lookAt((0, 0, 0.9))
        # Turn off shadows until we have fix for
        # https://bugs.launchpad.net/panda3d/+bug/1212752
        # keylight.setShadowCaster(True, 512, 512)

        sunlight = PointLight('sunlight')
        self._insertLight(
            sunlight,
            colour=(1, 1, 1, 1),
            pos=(1, -2, 20),
        )

        self._insertLight(
            AmbientLight('ambientLight'),
            colour=(.25, .25, .25, 1),
        )

    def _insertLight(self, light, pos=None, colour=None):

        if colour:
            light.setColor(colour)

        render = self.app.panda.render
        nodepath = self.reparent(NodePath(light), render)
        render.setLight(nodepath)

        if pos:
            nodepath.setPos(pos)

        return nodepath

    def setupMainMenu(self):
        self.mainMenuNode = self.reparent(
            NodePath('mainMenu'), self.app.panda.plaque)
        self.visibleNode = self.mainMenuNode

        self.button('play', self.showJoin, left=-0.87, z=0.25, scale=1.5)
        self.button(
            'servers', self.showServers, left=-0.83, z=0.16, scale=0.85)
        self.button(
            'practise', self.practiseClicked, left=-0.83, z=0.08, scale=0.85)
        self.button('archives', self.showArchives, left=-0.87, z=-0.1)
        self.button('settings', self.showSettings, left=-0.87, z=-0.25)
        self.button('credits', self.showCredits, left=-0.87, z=-0.4)
        self.button('exit', self.app.stop, right=0.87, z=-0.67)

    def setupCredits(self):
        self.creditsReel = CreditsReel(self.app)
        self.creditsNode = self.reparent(
            NodePath('credits'), self.app.panda.plaque)
        self.creditsNode.hide()

        self.button(
            'back to main menu', self.showMainMenu, right=0.87, z=-0.67,
            parent=self.creditsNode,
        )

    def setupSettings(self):
        self.settingsNode = self.reparent(
            NodePath('settings'), self.app.panda.plaque)
        self.settingsNode.hide()

        self.settingsScreen.setup(self.settingsNode)

    def setupArchives(self):
        self.archivesNode = self.reparent(
            NodePath('archives'), self.app.panda.plaque)
        self.archivesNode.hide()

        self.archivesScreen.setup(self.archivesNode)

    def setupServers(self):
        self.serversNode = self.reparent(
            NodePath('servers'), self.app.panda.plaque)
        self.serversNode.hide()

        self.serversScreen.setup(self.serversNode)

    def setupJoin(self):
        self.joinNode = self.reparent(NodePath('join'), self.app.panda.plaque)
        self.joinNode.hide()

        self.joinScreen.setup(self.joinNode)

    def button(self, text, onClick, scale=1.0, parent=None,
               textAlign=TextNode.A_left, **alignArgs):
        if parent is None:
            parent = self.mainMenuNode

        colours = self.app.theme.colours
        result = DirectButton(
            text=text,
            text_fg=colours.mainMenuColour,
            text1_fg=colours.mainMenuClicked,
            text2_fg=colours.mainMenuHighlight,
            text3_fg=colours.disabledButton,
            scale=scale*0.08,
            command=onClick,
            parent=parent,
            relief=None,
            textMayChange=True,
            text_align=textAlign,
        )
        align(result, **alignArgs)
        self.addDirect(result)
        return result

    def practiseClicked(self):
        db = self.app.layoutDatabase

        SIZE = (3, 1)
        AICOUNT = 5

        game = LocalGame(db, SIZE[0], SIZE[1], onceOnly=True)

        for i in range(AICOUNT):
            game.addBot('ranger')

        self.app.connector.openGameObject(game)


class JoinScreenHelper(object):
    def __init__(self, app, scene):
        self.app = app
        self.scene = scene

        self.joinLogBox = None
        self.playConnector = None

    def stop(self):
        self.playConnector.cancel()

    def show(self, servers=None):
        promptToHost = (servers is None)

        while len(self.joinLogBox['items']):
            self.joinLogBox.removeItem(self.joinLogBox['items'][0])

        if servers is None:
            servers = [const.JOIN_LOCAL_GAME]
            if self.app.connectionSettings.lanGames == 'beforeinet':
                servers.append(const.JOIN_LAN_GAME)
            servers += list(self.app.connectionSettings.servers)
            if self.app.connectionSettings.lanGames == 'afterinet':
                servers.append(const.JOIN_LAN_GAME)
            if self.app.connectionSettings.createGames:
                servers.append(const.CREATE_GAME)

        self.playConnector.begin(tuple(servers), promptToHost)

    def setup(self, joinNode):
        self.playConnector = PlayConnector(
            self.app,
            onSucceed=self.scene.showMainMenu,
            onFail=self.joinFailed,
            onLogLine=self.addJoinLogEntry,
            passwordGetFunction=self.getUserDetails,
            hostGameQueryFunction=self.askToHostGame,
        )

        colours = self.app.theme.colours
        self.joinLogBox = DirectScrolledList(
            decButton_text='',
            decButton_borderWidth=(0, 0),
            incButton_text='',
            incButton_borderWidth=(0, 0),

            pos=(-0.85, 0, 0.4),
            color=colours.joinScreenBackground,
            itemFrame_frameSize=(-0.05, 1.75, -0.888, 0.088),
            parent=joinNode,
            numItemsVisible=MAX_LOG_ITEMS,
        )
        self.joinLogBox.setTransparency(TransparencyAttrib.MAlpha)
        self.scene.button(
            'cancel', self.scene.showMainMenu, right=0.87, z=-0.67,
            parent=joinNode,
        )

    @defer.inlineCallbacks
    def joinFailed(self):
        yield self.scene.showOkDialog('Could not join any games')
        self.scene.showMainMenu()

    def getUserDetails(self, host, errorText=''):
        return ServerLoginDialogMaker(self.app).run(host, errorText)

    def askToHostGame(self):
        d = defer.Deferred()

        def gotResponse(result):
            dialog.cleanup()
            d.callback(result)

        dialog = YesNoDialog(
            dialogName='hostGameQuery',
            text='No games found. Host a game?',
            command=gotResponse,
            fadeScreen=0.3,
            button_pad=(0.1, 0.03),
            buttonPadSF=1.3,
        )
        dialog.show()
        return d

    def addJoinLogEntry(self, text):
        colours = self.app.theme.colours
        font = self.app.screenManager.fonts.consoleFont
        label = DirectLabel(
            text=text,
            text_scale=font.getPandaScale(),
            text_fg=colours.mainMenuColour,
            text_font=font.getPandaFont(self.app),
            text_align=TextNode.ALeft,
            relief=None,
        )
        while len(self.joinLogBox['items']) >= MAX_LOG_ITEMS:
            self.joinLogBox.removeItem(self.joinLogBox['items'][0])
        self.joinLogBox.addItem(label)


class ArchivesScreenHelper(object):
    def __init__(self, app, scene):
        self.app = app
        self.scene = scene
        self.archivist = Archivist()
        self.archivesGamesList = None
        self.archiveNameLabel = None
        self.archiveTimeLabel = None
        self.archiveDurationLabel = None
        self.archiveReplayButton = None
        self.archiveStatsButton = None
        self.selectedGameButton = None

    def show(self):
        self.archivist.refresh()

        self.selectedGameButton = None
        while self.archivesGamesList['items']:
            self.archivesGamesList.removeItem(
                self.archivesGamesList['items'][0])

        colours = self.app.theme.colours
        games = self.archivist.getGames()
        for game in games:
            gameName = os.path.splitext(os.path.basename(game.filename))[0]
            button = DirectButton(
                text=gameName,
                text_fg=colours.listboxButtons,
                text1_fg=colours.listboxSelectedButtons,
                text_align=TextNode.ALeft,
                scale=0.04,
                command=self.selectArchiveGame,
                relief=None,
            )
            button['extraArgs'] = [button]
            align(button, left=0)
            button.gameFile = game

            self.archivesGamesList.addItem(button)

        if games:
            self.selectArchiveGame(self.archivesGamesList['items'][0])
        else:
            self.archivesGamesList.addItem(DirectLabel(
                text='No compatible game files found',
                text_scale=0.04,
                text_fg=colours.noGamesColour,
                text_align=TextNode.ALeft,
                relief=None,
            ))

    def setup(self, archivesNode):
        button = DirectButton(
            text='Load replay from file...',
            scale=0.04,
            command=self.showLoadReplayFileDialog,
            parent=archivesNode,
            pad=(1, 0.3),
        )
        align(button, midX=0, top=0.45)

        label = DirectLabel(
            text='- or -',
            text_scale=0.06,
            text_align=TextNode.ACenter,
            relief=None,
            parent=archivesNode,
        )
        align(label, midX=0, top=0.33)

        colours = self.app.theme.colours
        self.archivesGamesList = DirectScrolledList(
            decButton_pos=(0.4, 0, 0.17),
            decButton_text='up',
            decButton_text_scale=0.04,
            decButton_borderWidth=(0.005, 0.005),
            decButton_pad=(0.03, 0.01),
            decButton_text3_fg=colours.disabledButton,

            incButton_pos=(0.4, 0, -0.51),
            incButton_text='down',
            incButton_text_scale=0.04,
            incButton_borderWidth=(0.005, 0.005),
            incButton_pad=(0.03, 0.01),
            incButton_text3_fg=colours.disabledButton,

            frameSize=(0.0, 0.8, -0.55, 0.22),
            frameColor=colours.replayMenu,
            pos=(-0.85, 0, 0),
            numItemsVisible=13,
            forceHeight=0.045,
            itemFrame_pos=(0.02, 0, 0.1),
            parent=archivesNode,
            )

        DirectButton(
            text='refresh',
            text_align=TextNode.ACenter,
            scale=0.04,
            command=self.show,
            parent=archivesNode,
            pad=(0.9, 0.3),
            pos=(-0.175, 0, 0.162),
        )

        frame = DirectFrame(
            parent=archivesNode,
            pos=(0.45, 0, 0.07),
            frameSize=(-0.4, 0.4, -0.09, 0.15),
            frameColor=colours.replayMenu,
        )

        self.archiveNameLabel = DirectLabel(
            parent=frame,
            text='',
            pos=(0, 0, 0.1),
            text_scale=0.04,
            text_fg=colours.listboxButtons,
            text_align=TextNode.ACenter,
            relief=None,
        )
        self.archiveTimeLabel = DirectLabel(
            parent=frame,
            text='No game selected',
            pos=(0, 0, 0.05),
            text_scale=0.04,
            text_fg=colours.listboxButtons,
            text_align=TextNode.ACenter,
            relief=None,
        )
        self.archiveDurationLabel = DirectLabel(
            parent=frame,
            text='',
            pos=(0, 0, -0.05),
            text_scale=0.04,
            text_fg=colours.listboxButtons,
            text_align=TextNode.ACenter,
            relief=None,
        )

        self.archiveReplayButton = DirectButton(
            text='Watch replay',
            text_align=TextNode.ACenter,
            scale=0.04,
            parent=archivesNode,
            pad=(0.9, 0.3),
            pos=(0.45, 0, -0.1),
            text3_fg=colours.disabledButton,
            command=self.watchSelectedReplay,
        )

        self.archiveStatsButton = DirectButton(
            text='View game statistics',
            text_align=TextNode.ACenter,
            scale=0.04,
            parent=archivesNode,
            pad=(0.9, 0.3),
            pos=(0.45, 0, -0.2),
            text3_fg=colours.disabledButton,
            command=self.viewSelectedGameStats,
        )

        self.scene.button(
            'back', self.scene.showMainMenu, right=0.87, z=-0.67,
            parent=archivesNode,
        )

    def showLoadReplayFileDialog(self):
        root = Tk()
        root.withdraw()
        tksupport.install(root)
        filename = askopenfilename(
            defaultextension='.trosrepl',
            filetypes=[
                ('Trosnoth replay', '*.trosrepl'),
            ],
            initialdir=getPath(user, replayDir),
            title='Select replay',
        )
        if filename:
            try:
                self.app.connector.openReplay(filename)
            except ReplayFileError:
                self.showReplayFileError()
            except:
                log.exception('Error while opening replay file')
                self.showReplayFileError()

    def showReplayFileError(self):
        self.scene.showOkDialog('Invalid file format')

    def watchSelectedReplay(self):
        if not self.selectedGameButton:
            return
        game = self.selectedGameButton.gameFile
        self.app.connector.openReplay(game.replayFilename)

    def viewSelectedGameStats(self):
        if not self.selectedGameButton:
            return
        game = self.selectedGameButton.gameFile
        game.viewStats(self.app)

    def selectArchiveGame(self, button):
        colours = self.app.theme.colours
        if self.selectedGameButton:
            self.selectedGameButton['text_fg'] = colours.listboxButtons

        self.selectedGameButton = button
        button['text_fg'] = colours.listboxSelectedButtons

        game = button.gameFile
        self.archiveNameLabel['text'] = game.alias

        dateTuple = [int(bit) for bit in game.dateTime.split(',')]
        self.archiveTimeLabel['text'] = time.strftime('%c', dateTuple)

        if not game.wasFinished():
            duration = 0
        else:
            dateUnix = time.mktime(dateTuple)
            lastUnix = game.gameFinishedTimestamp
            duration = max(0, int(lastUnix - dateUnix))

        if duration > 0:
            lengthMinutes, lengthSeconds = divmod(duration, 60)

            secPlural = '' if lengthSeconds == 1 else 's'
            minPlural = '' if lengthMinutes == 1 else 's'
            if lengthMinutes == 0:
                lengthString = '{} second{}'.format(lengthSeconds, secPlural)
            else:
                lengthString = '{} min{} {} sec{}'.format(
                    lengthMinutes, minPlural, lengthSeconds, secPlural)

            self.archiveDurationLabel['text'] = 'Duration: {}'.format(
                lengthString)
        else:
            self.archiveDurationLabel['text'] = ''

        self.archiveReplayButton['state'] = (
            DGG.NORMAL if game.hasReplay() else DGG.DISABLED)
        self.archiveStatsButton['state'] = (
            DGG.NORMAL if game.hasStats() else DGG.DISABLED)


class ServerLoginDialogMaker(object):
    USERNAME_CHARS = set(
        'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789-')

    def __init__(self, app):
        self.app = app
        self.d = None
        self.dialog = None
        self.createAccountVar = None

        self.retypeLabel = None
        self.retypeBox = None
        self.usernameBox = None
        self.passwordBox = None
        self.focus = None

        self.do = DirectObject()

    @defer.inlineCallbacks
    def run(self, host, errorText=''):
        if errorText:
            yield self.showError(errorText)
        result = yield self._runMainDialog(host)
        defer.returnValue(result)

    def showError(self, text):
        if self.dialog:
            self.dialog.hide()
            self._unlinkHotkeys()

        def ok(result):
            dialog.cleanup()
            if self.dialog:
                self.dialog.show()
                self._linkHotkeys()
            d.callback(None)

        d = defer.Deferred()
        dialog = OkDialog(
            dialogName='joinError',
            text=text,
            command=ok,
            fadeScreen=0.3,
            button_pad=(0.1, 0.03),
            buttonPadSF=1.3,
        )
        dialog.show()
        return d

    def cancel(self):
        self.dialog.cleanup()
        self._unlinkHotkeys()
        self.dialog = None
        self.d = None

    def _linkHotkeys(self):
        self.do.accept('tab', self._tabPressed)
        self.do.accept('shift-tab', self._shiftTabPressed)
        self.do.accept('enter', self._enterPressed)

    def _setFocus(self, field):
        field['focus'] = True
        self.focus = field

    def _tabPressed(self):
        if self.focus is self.usernameBox:
            self._setFocus(self.passwordBox)
        elif self.focus is self.passwordBox and self.createAccountVar[0]:
            self._setFocus(self.retypeBox)
        else:
            self._setFocus(self.usernameBox)

    def _shiftTabPressed(self):
        if self.focus is self.passwordBox:
            self._setFocus(self.usernameBox)
        elif self.focus is self.usernameBox and self.createAccountVar[0]:
            self._setFocus(self.retypeBox)
        else:
            self._setFocus(self.passwordBox)

    def _enterPressed(self):
        self._buttonPressed(DGG.DIALOG_OK)

    def _unlinkHotkeys(self):
        self.do.ignoreAll()

    def _buttonPressed(self, result):
        if result == DGG.DIALOG_CANCEL:
            self._cleanupAndReturn(None)
            return

        username = self.usernameBox.get()
        if not username:
            self.showError('You must give a username!')
            return

        createAccount = self.createAccountVar[0]
        password = self.passwordBox.get()

        if createAccount:
            if any(c not in self.USERNAME_CHARS for c in username):
                self.showError('Invalid username!')
                return
            if password != self.retypeBox.get():
                self.showError('Passwords do not match!')
                return

        if not password:
            self.showError('Password cannot be blank!')
            return

        self.app.identitySettings.usernames[self.host] = username
        self._cleanupAndReturn((createAccount, username, password))

    def _cleanupAndReturn(self, value):
        self._unlinkHotkeys()
        self.dialog.cleanup()
        self.dialog = None

        d, self.d = self.d, None
        d.callback(value)

    def _radioChanged(self):
        if self.createAccountVar[0]:
            self.retypeLabel.show()
            self.retypeBox.show()
            self.retypeBox.enterText('')
        else:
            self.retypeLabel.hide()
            self.retypeBox.hide()

        if self.usernameBox.get() == '':
            self._setFocus(self.usernameBox)
        elif self.passwordBox.get() == '' or not self.createAccountVar[0]:
            self._setFocus(self.passwordBox)
        else:
            self._setFocus(self.retypeBox)

    def _runMainDialog(self, host):
        if self.d is not None:
            raise RuntimeError('already running')
        self.d = defer.Deferred()
        self.host = host

        self.dialog = OkCancelDialog(
            dialogName='hostGameQuery',
            command=self._buttonPressed,
            fadeScreen=0.3,
            button_pad=(0.1, 0.03),
            buttonPadSF=1.2,
            topPad=0.5,
            midPad=0.4,
            sidePad=0.42,
            pad=(0.05, 0.03),
        )

        DirectLabel(
            parent=self.dialog,
            text=host,
            text_scale=0.1,
            text_align=TextNode.ACenter,
            pos=(0, 0, 0.42),
        )

        def makeEntryField(caption, z, obscured):
            label = DirectLabel(
                parent=self.dialog,
                text=caption,
                text_scale=0.05,
                text_align=TextNode.ALeft,
                pos=(-0.82, 0, z + 0.1),
            )
            entry = DirectEntry(
                parent=self.dialog,
                scale=0.05,
                width=32,
                pos=(-0.8, 0, z),
                pad=(0.2, 0.1),
                obscured=obscured,
                relief=DGG.GROOVE,
            )
            return label, entry

        discard, self.usernameBox = makeEntryField('Uesrname', 0.1, False)
        discard, self.passwordBox = makeEntryField('Password', -0.1, True)
        self.retypeLabel, self.retypeBox = makeEntryField(
            'Retype password', -0.3, True)

        def makeRadioButton(text, x, value):
            return DirectRadioButton(
                parent=self.dialog,
                text=text,
                variable=self.createAccountVar,
                value=[value],
                scale=0.05,
                text_align=TextNode.ACenter,
                pos=(x, 0, 0.32),
                pad=(0.2, 0.1),
                relief=None,
                command=self._radioChanged,
            )

        self.createAccountVar = [False]
        radioButtons = [
            makeRadioButton('Sign in', -0.3, False),
            makeRadioButton('New account', 0.3, True),
        ]
        for button in radioButtons:
            button.setOthers(radioButtons)

        username = self.app.identitySettings.usernames.get(host)
        if username is not None:
            self.usernameBox.enterText(username)
            self._setFocus(self.passwordBox)
        else:
            self._setFocus(self.usernameBox)

        self._linkHotkeys()
        self.dialog.show()
        return self.d


class ServersScreenHelper(object):
    def __init__(self, app, scene):
        self.app = app
        self.scene = scene
        self.serversList = None
        self.focusFrame = None

    def makeTextBox(self, frame, text, invalid=False):
        colours = self.app.theme.colours
        if invalid:
            colour = colours.invalidServerEntry
        else:
            colour = colours.serverEntry
        result = DirectEntry(
            parent=frame,
            scale=0.04,
            width=12,
            pos=(-0.5, 0, 0),
            pad=(0.2, 0.1),
            text_fg=colour,
            frameColor=(1, 1, 1, 1),
            initialText=text,
            focusInCommand=self.textBoxEntered,
            focusInExtraArgs=[frame],
            focusOutCommand=self.textBoxExited,
            focusOutExtraArgs=[frame],
        )
        result.entryInvalid = invalid
        return result

    def _makeFrame(self, new=False):
        result = DirectFrame(
            frameSize=(-0.5, 0.5, -0.05, 0.05),
            relief=None,
        )
        result.new = new
        return result

    def _littleButton(
            self, frame, text, x, font=None, command=None, extraArgs=None):
        colours = self.app.theme.colours
        return DirectButton(
            parent=frame,
            text=text,
            text_align=TextNode.ACenter,
            text_font=font,
            scale=0.04,
            pad=(0.9, 0.3),
            pos=(x, 0, 0),

            command=command,
            extraArgs=extraArgs,

            text_fg=colours.mainMenuColour,
            text1_fg=colours.mainMenuClicked,
            text2_fg=colours.mainMenuHighlight,
            text3_fg=colours.disabledButton,
            relief=None,
        )

    def _addFrameDecoration(self, frame):
        self._littleButton(
            frame, '[play]', 0.06,
            command=self.playClicked, extraArgs=[frame])
        self._littleButton(frame, '[account]', 0.21)

        gFont = self.app.screenManager.fonts.glyphFont
        gFont = gFont.getPandaFont(self.app)
        self._littleButton(
            frame, '[▲]', 0.34, gFont,
            command=self.moveServerUp, extraArgs=[frame])
        self._littleButton(
            frame, '[▼]', 0.42, gFont,
            command=self.moveServerDown, extraArgs=[frame])
        self._littleButton(
            frame, '[⊗]', 0.50, gFont,
            command=self.deleteServer, extraArgs=[frame])

    def show(self):
        while self.serversList['items']:
            self.serversList.removeItem(self.serversList['items'][0])

        connSettings = self.app.connectionSettings
        for host, port in connSettings.servers:
            frame = self._makeFrame()
            frame.server = self.makeTextBox(
                frame, self.getServerString(host, port))
            self._addFrameDecoration(frame)

            self.serversList.addItem(frame)

        self._addFrameForNewServer()

        self.lanDiscoveryBox['indicatorValue'] = (
            connSettings.lanGames != 'never')
        self.createRemoteBox['indicatorValue'] = connSettings.createGames

    def _addFrameForNewServer(self):
        frame = self._makeFrame(new=True)
        frame.server = self.makeTextBox(frame, '')
        self.serversList.addItem(frame)

    def promoteNewFrameToFullFrame(self, frame):
        if not frame.new:
            return
        self._addFrameDecoration(frame)
        frame.new = False

        self._addFrameForNewServer()

    def getServerString(self, host, port):
        if port == const.DEFAULT_SERVER_PORT:
            return host
        return '{}:{}'.format(host, port)

    def getHostAndPort(self, serverString):
        if ':' not in serverString:
            return serverString, const.DEFAULT_SERVER_PORT

        host, port = serverString.rsplit(':', 1)
        if ':' in host or not port.isdigit():
            return None, None
        return host, int(port)

    def playClicked(self, frame):
        self.validateFocusEntry()
        host, port = self.getHostAndPort(frame.server.get())
        if port is None or port > 65535 or not host:
            self.scene.showOkDialog('Invalid server string')
            return

        servers = [(host, port, '')]
        if self.app.connectionSettings.createGames:
            servers.append(const.CREATE_GAME)

        self.scene.showJoin(servers)

    def playLanGame(self):
        self.scene.showJoin([const.JOIN_LAN_GAME])

    def moveServerUp(self, frame):
        items = self.serversList['items']
        index = items.index(frame)
        if index > 0:
            items.pop(index)
            items.insert(index - 1, frame)
            self.serversList.refresh()
            self.save()

    def moveServerDown(self, frame):
        items = self.serversList['items']
        index = items.index(frame)
        newServerEntryIndex = len(items) - 1
        if index < newServerEntryIndex - 1:
            items.pop(index)
            items.insert(index + 1, frame)
            self.serversList.refresh()
            self.save()

    def deleteServer(self, frame):
        self.serversList.removeItem(frame)
        self.save()

    def validateFocusEntry(self):
        if self.focusFrame is not None:
            self.textBoxExited(self.focusFrame)

    def textBoxEntered(self, frame):
        self.focusFrame = frame
        if frame.new:
            self.promoteNewFrameToFullFrame(frame)

    def textBoxExited(self, frame):
        self.save()

        entry = frame.server.get()
        host, port = self.getHostAndPort(entry)

        # Detaching and recreating the DirectEntry is ugly but I couldn't find
        # a straightforward way of changing the text colour and making it
        # refresh. --talljosh 2016-08-03
        if port is None or port > 65535:
            if not frame.server.entryInvalid:
                frame.server.detachNode()
                frame.server = self.makeTextBox(frame, entry, invalid=True)
            return
        if frame.server.entryInvalid:
            frame.server.detachNode()
            frame.server = self.makeTextBox(frame, entry)

    def setup(self, serversNode):
        colours = self.app.theme.colours
        frame = DirectFrame(
            parent=serversNode,
            pos=(0, 0, 0),
            frameSize=(-0.9, 0.9, -0.55, 0.45),
            frameColor=colours.playMenu,
            relief=DGG.GROOVE,
            borderWidth=(0.02, 0.02),
        )

        self.serversList = DirectScrolledList(
            decButton_pos=(0, 0, 0.35),
            decButton_text='up',
            decButton_text_scale=0.04,
            decButton_borderWidth=(0.005, 0.005),
            decButton_pad=(0.03, 0.01),
            decButton_text3_fg=colours.disabledButton,

            incButton_pos=(0, 0, -0.45),
            incButton_text='down',
            incButton_text_scale=0.04,
            incButton_borderWidth=(0.005, 0.005),
            incButton_pad=(0.03, 0.01),
            incButton_text3_fg=colours.disabledButton,

            frameSize=(-0.55, 0.55, -0.5, 0.4),
            relief=DGG.SUNKEN,
            borderWidth=(0.005, 0.005),
            pos=(-0.3, 0, 0),
            numItemsVisible=7,
            forceHeight=0.1,
            itemFrame_pos=(0, 0, 0.26),
            parent=frame,
            )

        self.createRemoteBox = self._checkBox(
            frame, 'Create remote games', 0.35)
        self.lanDiscoveryBox = self._checkBox(frame, 'LAN discovery', 0.28)
        DirectButton(
            parent=frame,
            text='Search LAN now',
            scale=0.04,
            command=self.playLanGame,
            text_align=TextNode.ACenter,
            pad=(0.9, 0.3),
            pos=(0.55, 0, 0.15),
        )

        self.scene.button(
            'done', self.doneClicked, right=0.87, z=-0.67,
            parent=serversNode,
        )

    def _checkBox(self, parent, text, y):
        colours = self.app.theme.colours
        label = DirectLabel(
            parent=parent,
            text=text,
            text_scale=0.04,
            text_fg=colours.listboxButtons,
            relief=None,
        )
        align(label, left=0.38, midZ=y)

        result = DirectCheckButton(
            parent=parent,
            scale=0.04,
            pos=(0.35, 0, y),
            command=self.checkBoxChanged,
        )
        return result

    def checkBoxChanged(self, newValue):
        self.save()

    def doneClicked(self):
        self.save()
        self.scene.showMainMenu()

    def save(self):
        connectionSettings = self.app.connectionSettings

        connectionSettings.servers = [
            self.getHostAndPort(frame.server.get())
            for frame in self.serversList['items']
            if not frame.new]
        connectionSettings.createGames = self.createRemoteBox[
            'indicatorValue']
        connectionSettings.lanGames = (
            'afterinet' if self.lanDiscoveryBox['indicatorValue'] else
            'never')
        connectionSettings.save()


class CreditsReel(object):
    '''
    Creates a Panda scene that's independent of the main render tree, so that
    the credits can be displayed in a smaller display region within the main
    screen.
    '''

    def __init__(self, app):
        self.app = app
        self.do = DirectObject()

        self.running = False
        self.displayRegion = None
        self.root = NodePath('creditsRender')
        self.camera = Camera('creditsCam')
        self.cameraNP = NodePath(self.camera)

        # Set parameters to match those of render2d
        self.root.setDepthTest(0)
        self.root.setDepthWrite(0)
        self.root.setMaterialOff(1)
        self.root.setTwoSided(1)

        self.aspect2d = self.root # self.root.attachNewNode('creditsAspect')

        lens = OrthographicLens()
        lens.setFilmSize(2, 2)
        lens.setFilmOffset(0, 0)
        lens.setNearFar(-1000, 1000)
        self.camera.setLens(lens)

        self.cameraNP.reparentTo(self.root)

        self.scrollTask = None
        self.lastTime = None
        self.creditsFileLoaded = False

    def loadCreditsFileIfNeeded(self):
        if self.creditsFileLoaded:
            return

        filePath = getPath(startupMenu, 'credits3d.txt')
        with codecs.open(filePath, 'rU', encoding='utf-8') as f:
            creditsLines = f.read().splitlines()

        y = 0
        for line in creditsLines:
            if line.startswith('!!'):
                font = self.app.fonts.creditsH1
                line = line[len('!!'):]
            elif line.startswith('!'):
                font = self.app.fonts.creditsH2
                line = line[len('!'):]
            else:
                font = self.app.fonts.creditsFont

            lineHeight = font.getPandaLineHeight(self.app)
            node = font.makeOnscreenText(
                self.app,
                text=line or ' ',       # Prevents .getNumRows() bug
                fg=self.app.theme.colours.mainMenuColour,
                align=TextNode.ACenter,
                pos=(0, y - lineHeight),
                parent=self.aspect2d,
                wordwrap=28,
            )
            y -= lineHeight * (node.textNode.getNumRows() + 0.2)

        self.creditsFileLoaded = True

    def stop(self):
        if not self.running:
            return
        self.running = False
        self.do.ignoreAll()

        if self.scrollTask is not None:
            self.app.panda.taskMgr.remove(self.scrollTask)
            self.scrollTask = None

        if self.displayRegion is not None:
            self.displayRegion.setActive(False)

    def start(self):
        self.cameraNP.setPos((0, 0, 0))
        if self.running:
            return
        self.running = True

        self.loadCreditsFileIfNeeded()

        if self.scrollTask is None:
            self.scrollTask = self.app.panda.taskMgr.add(
                self.updateCredits, 'creditsLoop')
            self.lastTime = self.scrollTask.time

        if self.displayRegion is None:
            self.displayRegion = self.app.panda.win.makeDisplayRegion()
            self.displayRegion.setSort(5)
            self.displayRegion.setClearDepthActive(1)
            self.displayRegion.setIncompleteRender(False)
            self.displayRegion.setCamera(self.cameraNP)

        self.displayRegion.setActive(True)
        self.do.accept('aspectRatioChanged', self.aspectRatioChanged)
        self.aspectRatioChanged()

    def aspectRatioChanged(self):
        # Scaling from -1 to +1
        idealTop = 0.66
        idealBottom = -0.74

        aspectRatio = self.app.panda.getAspectRatio()
        top = idealTop * min(aspectRatio * 3. / 4, 1)
        bottom = idealBottom * min(aspectRatio * 3. / 4, 1)

        self.displayRegion.setDimensions(
            0, 1, 0.5 * (1 + bottom), 0.5 * (1 + top))

        windowRatio = 2 * aspectRatio / (top - bottom)

        self.cameraNP.setScale(windowRatio * 3. / 4, 1.0, 1.0)

    def updateCredits(self, task):
        deltaT = task.time - self.lastTime
        self.lastTime = task.time

        z = self.cameraNP.getZ()
        z -= deltaT * CREDITS_SCROLL_SPEED
        self.cameraNP.setZ(z)
        return Task.cont
