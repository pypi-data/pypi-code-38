import random

from trosnoth.bots.goalsetter import (
    GoalSetterBot, MessAroundInZone, Goal, RespawnNearZone,
)


class OneZoneBot(GoalSetterBot):
    nick = 'Bothersome'
    generic = True

    class MainGoalClass(Goal):
        def reevaluate(self):
            if self.bot.player.dead:
                zone = self.bot.player.getZone()
                if zone is None:
                    zone = random.choice(list(self.bot.world.zones))
                self.setSubGoal(RespawnNearZone(self.bot, self, zone))
            else:
                self.setSubGoal(MessAroundInZone(self.bot, self))


    def start(self):
        super(OneZoneBot, self).start()

        self.setDodgesBullets(False)
        self.setUpgradePolicy(None)


BotClass = OneZoneBot
