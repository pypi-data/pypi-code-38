import logging
import random

from trosnoth.bots.goalsetter import GoalSetterBot, Goal, MessAroundInZone

log = logging.getLogger(__name__)


class BravelyRunAway(Goal):
    '''
    He was not at all afraid to be killed in nasty ways,
    Brave, brave, brave, brave Sir Robin!
    '''

    def __init__(self, bot, parent):
        super(BravelyRunAway, self).__init__(bot, parent)
        self.nextCheck = None
        self.messing = False

    def start(self):
        self.bot.setAggression(False)
        self.bot.setDodgesBullets(True)

        self.bot.onOrderFinished.addListener(self.orderFinished)
        self.bot.onTick.addListener(self.tick)
        super(BravelyRunAway, self).start()
        self.scheduleNextCheck()

    def stop(self):
        super(BravelyRunAway, self).stop()
        self.bot.onOrderFinished.removeListener(self.orderFinished)
        self.bot.onTick.removeListener(self.tick)
        self.cancelNextCheck()

    def scheduleNextCheck(self):
        self.cancelNextCheck()
        self.nextCheck = self.bot.world.callLater(5, self.reevaluate)

    def cancelNextCheck(self):
        if self.nextCheck:
            self.nextCheck.cancel()
            self.nextCheck = None

    def tick(self):
        if self.messing and self.inScaryZone():
            self.reevaluate()

    def orderFinished(self):
        self.reevaluate()

    def reevaluate(self):
        self.cancelNextCheck()
        self.messing = False

        if self.bot.player.dead:
            self.setSubGoal(RespawnFarAway(self.bot, self))
            return

        if self.inScaryZone():
            self.runAway()
        else:
            self.messing = True
            self.setSubGoal(MessAroundInZone(self.bot, self))
        self.scheduleNextCheck()

    def inScaryZone(self):
        thisPlayer = self.bot.player
        zone = thisPlayer.getZone()
        if zone is None:
            return True
        return any(not thisPlayer.isFriendsWith(p) for p in zone.players)

    def runAway(self):
        player = self.bot.player
        curZone = player.getZone()
        neighbours = list(curZone.getUnblockedNeighbours())
        if curZone is None:
            targetZone = random.choice(list(self.bot.world.zones))
        elif not neighbours:
            targetZone = curZone
        else:
            targetZone = getBestZone(player, neighbours)

        self.setSubGoal(None)
        self.bot.moveToOrb(targetZone)


def getBestZone(player, zones, prefer=None):
    enemiesByZone = {
        z: sum(not player.isFriendsWith(p) for p in z.players)
        for z in zones
    }
    minEnemies = min(enemiesByZone.values())
    okZones = [z for z in zones if enemiesByZone[z] == minEnemies]
    if prefer and prefer in okZones:
        return prefer
    return random.choice(okZones)


class RespawnFarAway(Goal):
    '''
    Respawns somewhere away from enemies.
    '''

    def start(self):
        self.bot.onOrderFinished.addListener(self.orderFinished)
        super(RespawnFarAway, self).start()

    def stop(self):
        super(RespawnFarAway, self).stop()
        self.bot.onOrderFinished.removeListener(self.orderFinished)

    def orderFinished(self):
        self.reevaluate()

    def reevaluate(self):
        player = self.bot.player
        if not player.dead:
            self.returnToParent()
            return

        curZone = player.getZone()
        okZones = [
            z for z in self.bot.world.zones
            if player.isZoneRespawnable(z)]
        zone = getBestZone(player, okZones, prefer=curZone)

        if zone != curZone:
            self.bot.moveToOrb(zone)
            return

        if player.timeTillRespawn > 0:
            self.bot.world.callLater(player.timeTillRespawn, self.reevaluate)
        else:
            self.bot.respawn()




class SirRobinBot(GoalSetterBot):
    nick = 'SirRobinBot'
    generic = True

    MainGoalClass = BravelyRunAway


BotClass = SirRobinBot
