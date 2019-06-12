from trosnoth.bots.base import Bot

from trosnoth.messages import TickMsg
from trosnoth.model.upgrades import Grenade
from trosnoth.utils.math import distance


class JohnBot(Bot):
    '''
    This is not the original JohnAI, as the bot API has changed substantially
    since JohnAI was written. Instead, this bot is inspired by version 1.1.3 of
    JohnAI, last edited 2010-12-28. It maintains the following behaviours of
    the original JohnAI:
     - Chases and shoots at nearby enemies.
     - Uses grenades when there are 3 or more enemies in the zone
    '''

    nick = 'JohnBot'
    generic = True

    def start(self):
        super(JohnBot, self).start()

        self.orderFinished()

    def orderFinished(self):
        if self.player.dead:
            if self.player.inRespawnableZone():
                self.respawn()
            else:
                self.moveToFriendlyZone()

        else:
            self.startMoving()

    @TickMsg.handler
    def handle_TickMsg(self, msg):
        super(JohnBot, self).handle_TickMsg(msg)

        if self.player.dead:
            return
        zone = self.player.getZone()
        if not zone:
            return

        enemyPlayers = len([
            p for p in zone.players
            if not (p.dead or self.player.isFriendsWith(p))])
        if enemyPlayers >= 3:
            self.setUpgradePolicy(Grenade)
        else:
            self.setUpgradePolicy(None)

    def moveToFriendlyZone(self):
        zones = [
            z for z in self.world.zones if
            self.player.isZoneRespawnable(z)]
        if not zones:
            self.world.callLater(3, self.orderFinished)
            return

        playerPos = self.player.pos
        bestZone = min(zones, key=lambda z: distance(z.defn.pos, playerPos))
        self.moveToZone(bestZone)

    def startMoving(self):
        enemies = [
            p for p in self.world.players
            if not (p.dead or self.player.isFriendsWith(p))]
        playerPos = self.player.pos

        if enemies:
            nearestEnemy = min(
                enemies, key=lambda p: distance(p.pos, playerPos))
            self.attackPlayer(nearestEnemy)
        else:
            zones = [
                z for z in self.world.zones
                if z.owner != self.player.team and
                z.adjacentToAnotherZoneOwnedBy(self.player.team)]
            if zones:
                nearestZone = min(
                    zones, key=lambda z: distance(z.defn.pos, playerPos))
                self.moveToOrb(nearestZone)
            else:
                self.world.callLater(3, self.orderFinished)


BotClass = JohnBot
