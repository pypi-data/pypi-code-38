import logging
from twisted.internet import task

from direct.showbase import ShowBase
from direct.showbase.DirectObject import DirectObject
from panda3d.core import loadPrcFile, NodePath, loadPrcFileData
from trosnoth.client3d.base.screenManager import screenManager
from trosnoth.client3d.base.screenManager.screenManager import NO_BORDER
from trosnoth.client3d.base.sound.soundPlayer import SoundPlayer

from trosnoth import data
from trosnoth.client3d.base.sound.musicManager import MusicManager
from trosnoth.client3d.appsettings import (
    DisplaySettings, SoundSettings,IdentitySettings,  ConnectionSettings,
    KeyboardMapping,
)
from trosnoth.client3d.themes import Theme
from trosnoth.manholehelper import LocalManholeHelper
from trosnoth.utils.utils import timeNow

log = logging.getLogger(__name__)


class Application(object):
    '''Instantiating the Main class will set up a ui. Calling the run()
    method will run the application.'''

    do = None

    def __init__(self, caption):
        '''Initialise the application.'''
        self.caption = caption

        self.displaySettings = DisplaySettings(self)
        self.initPanda()

        self.soundSettings = SoundSettings(self)
        self.identitySettings = IdentitySettings(self)
        self.connectionSettings = ConnectionSettings(self)
        self.keymap = KeyboardMapping(self)

        self._initSound()

        self.screenManager = screenManager.ScreenManager(
            self, self.displaySettings.size,
            self.displaySettings.displayMode, caption)
        self.fonts = self.screenManager.fonts
        self.initialise()
        self._running = False
        self.lastTime = None
        self.game = None

        self.initPanda()

    def getConsoleLocals(self):
        return {
            'helper': LocalManholeHelper(lambda: self.game),
            'game': self.game,
        }

    def _initSound(self):
        self.musicManager = MusicManager(self)
        self.soundPlayer = SoundPlayer(self)

        # Set the master sound volume.
        self.soundSettings.apply()

    def initPanda(self):
        if hasattr(self, 'panda'):
            # Allow multiple entry
            return
        if self.do is None:
            self.do = DirectObject()

        # The undecorated config option can't be changed at runtime, so we need
        # to set it before the panda object is created.
        if self.displaySettings.displayMode == NO_BORDER:
            loadPrcFileData('', 'undecorated 1')

        # The resolution /can/ be changed at runtime, but there's a split second
        # flash of the window at the defualt resolution when first opening the
        # game which looks quite ugly.
        loadPrcFileData('', 'win-size %d %d' % self.displaySettings.size)

        loadPrcFile(data.getPandaPath(data, 'config/config.prc'))
        self.panda = ShowBase.ShowBase()
        self.pandaScene = None

        # See https://www.panda3d.org/manual/index.php/Mouse_Support
        self.panda.disableMouse()    # Name is misleading

        self.displaySettings.applyTimings()

        self.initPlaque()

        self.displaySettings.onDetailLevelChanged.addListener(self.setShader)
        self.setShader()

    def setShader(self):
        if self.displaySettings.shader:
            self.panda.render.setShaderAuto()
        else:
            self.panda.render.setShaderOff()

    def initPlaque(self):
        '''
        Sets up a node in panda's 2D scene graph that represent a 4:3
        rectangle that is always entirely visible regardless of the window
        aspect ratio. This is useful for menus. Within the plaque, x
        coordinates run from -1 to 1, and z coordinates run from -0.75 to 0.75.
        '''
        self.panda.plaque = self.panda.aspect2d.attachNewNode('plaque')
        self.do.accept('aspectRatioChanged', self.aspectRatioChanged)

    def aspectRatioChanged(self):
        '''
        Called when the aspect ratio of the panda window changes. We use this
        to move the handles on the 4:3 plaque.
        '''
        aspectRatio = self.panda.getAspectRatio()
        scale = max(1.0, min(4. / 3, aspectRatio))
        self.panda.plaque.setScale(scale, scale, scale)

    def initialise(self):
        '''
        Provides the opportunity for initialisation by subclasses before the
        interface element is created.
        '''
        self.theme = Theme(self)

    def getFontFilename(self, fontName):
        return self.theme.getPandaPath('fonts', fontName)

    def changeScreenSize(self, size, displayMode):
        self.screenManager.setScreenProperties(size, displayMode, self.caption)

    def run_twisted(self, reactor=None):
        '''Runs the application using Twisted's reactor.'''

        if reactor is None:
            from twisted.internet import reactor

        def _stop():
            if not self._running:
                if reactor.running:
                    log.warning(
                        'stop() called twice. Terminating immediately.')
                    reactor.stop()
                return

            self._running = False

            # Give time for shutdown sequence.
            reactor.callLater(0.3, reactor.stop)

        self._stop = _stop
        self.lastTime = self.lastFPSLog = timeNow()

        # panda stuff
        self.displayLoop = task.LoopingCall(self.displayStep, reactor)
        self.displayLoop.clock = reactor
        self.displayLoop.start(0)   # self-limiting

        self._running = True
        reactor.run()

    def displayStep(self, reactor):
        try:
            self.panda.taskMgr.step()
        except (SystemExit, KeyboardInterrupt):
            self.stop()
        except:
            log.exception('Error in panda3d task manager')

    def run_with_profiling(self, *args, **kwargs):
        import cProfile
        from trosnoth.utils.profiling import KCacheGrindOutputter

        try:
            from panda3d.core import PStatClient
            PStatClient.connect()
        except ImportError:
            pass

        prof = cProfile.Profile()

        try:
            prof.runcall(self.run_twisted, *args, **kwargs)
        except SystemExit:
            pass
        finally:
            kg = KCacheGrindOutputter(prof)
            with open('trosnoth.log', 'w') as f:
                kg.output(f)

    def stop(self):
        if self._running:
            self.stopping()
        self._stop()

    def tick(self):
        pass

    def stopping(self):
        '''Any finalisation which must happen before stopping the reactor.'''
        pass

    def setPandaScene(self, scene):
        '''
        Sets a special scene object as the controller for the panda3d
        interactions.
        '''
        if self.pandaScene:
            self.pandaScene.stop()

        self.pandaScene = scene

        if scene:
            scene.start()


class PandaScene(object):
    '''
    Base class for objects passed to app.setPandaScene().
    '''

    def __init__(self, app, *args, **kwargs):
        super(PandaScene, self).__init__(*args, **kwargs)
        self.app = app
        self.cleanupNodePaths = set()
        self.cleanupDirectObjects = set()

    def start(self):
        '''
        Sets up this panda scene. The panda parameter is a panda3d ShowBase
        object.
        '''
        raise NotImplementedError('{}.start()'.format(self.__class__.__name__))

    def stop(self):
        '''
        Called when the scene is changed away from this scene. Must clean up
        every part of the scene that has been set up. The default
        implementation is to remove any node paths in self.cleanupNodePaths and
        any objects in cleanupDirectObjects.
        '''
        while self.cleanupNodePaths:
            self.cleanupNodePaths.pop().removeNode()
        while self.cleanupDirectObjects:
            self.cleanupDirectObjects.pop().destroy()

    def reparent(self, nodePath, parent=None):
        '''
        Reparents the given node path into the given parent and records the
        node in self.cleanupNodePaths so that it will be cleaned up on scene
        exit.
        Returns the given node path.
        '''
        if parent is None:
            parent = self.app.panda.render
        nodePath.reparentTo(parent)
        self.cleanupNodePaths.add(nodePath)
        return nodePath

    def addDirect(self, directObject):
        '''
        Registers a directGUI object for destruction when this scene is hidden.
        '''
        self.cleanupDirectObjects.add(directObject)

    def insertLight(
            self, light, parent=None, pos=None, colour=None, targets=None,
            direction=None):
        '''
        Convenience function for positioning a light in the scene and applying
        it to objects.
        '''
        if parent is None:
            parent = self.app.panda.render
        if targets is None:
            targets = [self.app.panda.render]

        if colour:
            light.setColor(colour)
        if direction:
            light.setDirection(direction)

        nodepath = self.reparent(NodePath(light), parent)

        if pos:
            nodepath.setPos(pos)

        for target in targets:
            target.setLight(nodepath)

        return nodepath
