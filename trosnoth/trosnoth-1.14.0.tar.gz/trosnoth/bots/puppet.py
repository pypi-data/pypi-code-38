from trosnoth.bots.base import Bot
from trosnoth.utils.event import Event


class PuppetBot(Bot):
    '''
    Does nothing except when order methods (e.g. standStill(), moveToOrb()
    etc.) are manually called.
    '''

    nick = 'Puppet'

    def __init__(self, *args, **kwargs):
        super(PuppetBot, self).__init__(*args, **kwargs)
        self.onOrderFinished = Event([])

    def start(self):
        super(PuppetBot, self).start()

        self.setDodgesBullets(False)
        self.setUpgradePolicy(None)

    def orderFinished(self):
        '''
        Called by an order when it is complete or cannot continue further. May
        be overridden by subclasses.
        '''
        self.standStill()
        self.onOrderFinished()


BotClass = PuppetBot
