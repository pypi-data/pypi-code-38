if __name__ == '__main__':
    import os, sys
    sys.path.insert(0, os.path.join(
        os.path.abspath(os.path.dirname(__file__)), '..', '..'))

    # Install the asyncio reactor as early as possible
    import asyncio
    from twisted.internet import asyncioreactor
    asyncioreactor.install(asyncio.get_event_loop())


import logging
import random

from trosnoth.bots.base import Bot


log = logging.getLogger(__name__)


class PathTestBot(Bot):
    '''
    Chooses a human player. When that player shoots, the bot moves to where
    that player is.
    '''
    nick = 'PathTestBot'
    focus = None

    def start(self):
        super().start()

        self.setAggression(False)
        self.orderFinished()

    def orderFinished(self):
        if self.player.dead:
            zone = self.world.selectZoneForTeam(self.player.teamId)
            if not zone:
                zone = random.choice(list(self.world.zones))
            self.respawn(zone=zone)
            return

        if self.focus and self.focus not in self.world.players:
            self.setFocus(None)

        if self.focus is None:
            humans = [p for p in self.world.players if not p.bot]
            if humans:
                self.setFocus(random.choice(humans))
            else:
                self.world.callLater(1, self.orderFinished)
        self.standStill()

    def setFocus(self, focus):
        log.error('%s: set focus to %s', self.player.nick, focus)
        if self.focus:
            self.focus.onShotFired.removeListener(self.focusShotFired)
        self.focus = focus
        if focus:
            focus.onShotFired.addListener(self.focusShotFired)

    def focusShotFired(self, *args, **kwargs):
        log.error('%s: moving to %s', self.player.nick, self.focus.pos)
        self.moveToPoint(self.focus.pos)


BotClass = PathTestBot


if __name__ == '__main__':
    from trosnoth.levels.base import playLevel
    from trosnoth.levels.testing import TestingLevel
    playLevel(TestingLevel(
        halfMapWidth=3, mapHeight=2), aiCount=1, aiClass='pathtest')