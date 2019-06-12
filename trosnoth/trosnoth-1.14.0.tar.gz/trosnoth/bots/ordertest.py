import random

from trosnoth.bots.base import Bot
from trosnoth.model.upgrades import Shield


class OrderTestBot(Bot):
    '''
    Not a very sensible bot, just exists to test the system of giving bots
    orders.
    '''
    nick = 'TestingBot'

    def start(self):
        super(OrderTestBot, self).start()

        self.setAggression(False)
        self.setUpgradePolicy(Shield)

        self.orderFinished()

    def orderFinished(self):
        if self.player.dead:
            zones = [
                z for z in self.world.zones if z.owner == self.player.team]
            if not zones:
                zones = list(self.world.zones)
            self.respawn(zone=random.choice(zones))
        else:
            enemies = [
                p for p in self.world.players if p.team != self.player.team and
                not p.dead]
            if enemies:
                enemy = random.choice(enemies)
                # e,self.moveToPoint(enemy.pos)
                self.followPlayer(enemy)
            else:
                # self.world.callLater(1, self.orderFinished)
                self.moveToOrb(random.choice(list(self.world.zones)))
                # self.moveToZone(random.choice(list(self.world.zones)))


BotClass = OrderTestBot
