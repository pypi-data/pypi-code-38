import logging

import pygame

from .screenManager import screenManager, windowManager
from trosnoth.gui.sound.musicManager import MusicManager
from trosnoth.gui.sound.soundPlayer import SoundPlayer
from trosnoth.utils.utils import timeNow
from trosnoth.gui.errors import ApplicationExit

log = logging.getLogger(__name__)

TARGET_FRAME_RATE = 60.
LOG_FPS = False


class JitterLogger(object):
    def __init__(self, cycle):
        self.cycle = cycle
        self.lastTime = None
        self.thisCount = 0
        self.thisMax = 0
        self.jitter = None

    def noteGap(self):
        '''
        Called to tell the JitterLogger that there is currently a gap,
        so the timing of the next observation should be discarded.
        '''
        self.lastTime = None

    def observation(self, expectedTime, resume=False):
        if resume:
            self.noteGap()

        now = timeNow()
        if self.lastTime:
            value = now - self.lastTime - expectedTime
            self.thisMax = max(self.thisMax, value)
            self.thisCount += 1

            if self.thisCount >= self.cycle:
                self.jitter = self.thisMax
                self.thisCount = 0
                self.thisMax = 0

        self.lastTime = now


class Application(object):
    '''Instantiating the Main class will set up a ui. Calling the run()
    method will run the application.'''

    def __init__(self, size, fullScreen, caption, element):
        '''Initialise the application.'''
        self._options = (element, size, fullScreen, caption)
        self._initSound()
        self._makeScreenManager(element, size, fullScreen, caption)
        self.fonts = self.screenManager.fonts
        self.initialise()
        self.screenManager.createInterface(element)
        self._running = False
        self.lastTime = None
        self.lastFPSLog = None
        self.ticksSinceFPSLog = 0
        self.jitterLogger = JitterLogger(cycle=60)
        pygame.key.set_repeat(300, 30)

    def __getattr__(self, attr):
        if attr == 'interface':
            return self.screenManager.interface
        raise AttributeError(attr)

    def _initSound(self):
        self.musicManager = MusicManager()
        self.soundPlayer = SoundPlayer()

    def _makeScreenManager(self, element, size, fullScreen, caption):
        self.screenManager = screenManager.ScreenManager(
            self, size, fullScreen, caption)

    def restart(self):
        self._initSound()
        self._makeScreenManager(*self._options)
        self.fonts = self.screenManager.fonts
        self.initialise()
        self.screenManager.createInterface(self._options[0])

    def initialise(self):
        '''
        Provides the opportunity for initialisation by subclasses before the
        interface element is created.
        '''

    def getFontFilename(self, fontName):
        '''
        May be overridden by an application in order to provide a custom font
        location, or some other mapping from font name to filename.
        '''
        return fontName

    def run(self):
        '''Runs the application.'''
        def _stop():
            self._running = False
            raise ApplicationExit
        self._stop = _stop

        self._running = True
        self.lastTime = self.lastFPSLog = timeNow()
        while self._running:
            try:
                self.tick()
                self.doFlip()
            except ApplicationExit:
                break
        pygame.quit()

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

        self.jitterLogger.noteGap()
        self.targetFrameInterval = 1. / TARGET_FRAME_RATE
        reactor.callLater(self.targetFrameInterval, self.twisted_tick, reactor)
        self._running = True
        reactor.run()
        pygame.display.quit()
        pygame.quit()

    def run_with_profiling(self, twisted, *args, **kwargs):
        import cProfile
        from trosnoth.utils.profiling import KCacheGrindOutputter
        prof = cProfile.Profile()

        if twisted:
            mainFunction = self.run_twisted
        else:
            mainFunction = self.run

        try:
            prof.runcall(mainFunction, *args, **kwargs)
        except SystemExit:
            pass
        finally:
            kg = KCacheGrindOutputter(prof)
            with open('trosnoth.log', 'w') as f:
                kg.output(f)

    def twisted_tick(self, reactor):
        reactor.callLater(self.targetFrameInterval, self.twisted_tick, reactor)
        self.jitterLogger.observation(self.targetFrameInterval)
        self.tick()
        self.doFlip()

    def stop(self):
        if self._running:
            self.stopping()
        self._stop()

    def tick(self):
        try:
            self._tick()
        except ApplicationExit:
            raise
        except Exception:
            log.exception('Error during tick')

    def _tick(self):
        '''Processes the events in the pygame event queue, and causes the
        application to be updated, then refreshes the screen. This routine is
        called as often as possible - it is not limited to a specific frame
        rate.'''
        if not self._running:
            return

        now = timeNow()

        self.ticksSinceFPSLog += 1
        if LOG_FPS and now - self.lastFPSLog > 1:
            log.warning('%.2f FPS', self.ticksSinceFPSLog / (
                now - self.lastFPSLog))
            self.lastFPSLog = now
            self.ticksSinceFPSLog = 0

        # Process the events in the event queue.
        for event in pygame.event.get():
            try:
                event = self.musicManager.processEvent(event)
                if not self._running:
                    return
                if event is not None:
                    event = self.screenManager.processEvent(event)
                    if not self._running:
                        return
                    if event is not None:
                        # Special events.
                        if event.type == pygame.QUIT:
                            self.stop()
                            return
            except ApplicationExit:
                raise
            except Exception:
                log.exception('Error during Pygame event processing')
            if not self._running:
                return

        # Give things an opportunity to update their state.
        deltaT = now - self.lastTime
        self.lastTime = now
        try:
            self.screenManager.tick(deltaT)
        except ApplicationExit:
            raise
        except Exception:
            log.exception('Error drawing screen')

        if not self._running:
            return

        if pygame.display.get_active():
            # Update the screen.
            try:
                self.screenManager.draw(self.screenManager.screen)
            except pygame.error:
                # Surface may have been lost (DirectDraw error)
                log.exception('Error in screenManager.draw()')

    def doFlip(self):
        if self._running and pygame.display.get_active():
            # Flip the display.
            pygame.display.flip()

    def stopping(self):
        '''Any finalisation which must happen before stopping the reactor.'''
        self.screenManager.finalise()


class MultiWindowApplication(Application):

    def _makeScreenManager(self, element, size, fullScreen, caption):
        self.screenManager = windowManager.WindowManager(
            self, element, size, fullScreen, caption)
