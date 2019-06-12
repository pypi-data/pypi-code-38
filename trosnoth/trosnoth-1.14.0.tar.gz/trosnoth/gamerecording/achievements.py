import logging

from twisted.internet import defer

from trosnoth import dbqueue
from trosnoth.messages import AchievementUnlockedMsg
from trosnoth.utils.twist import WeakLoopingCall
from trosnoth.utils.utils import timeNow

from trosnoth.gamerecording.achievementlist import availableAchievements

log = logging.getLogger(__name__)


class PlayerAchievements(object):
    '''Tracks achievements for a single player.'''
    achievementDefs = availableAchievements

    def __init__(self, manager, player):
        self.manager = manager
        self.player = player
        self.world = manager.world
        self.achievements = {
            c.idstring: c(player, self.world)
            for c in self.achievementDefs.perPlayer
        }
        self.stopped = self.started = False
        self.savingProgress = False

    def rejoined(self, player):
        self.player = player
        for achievement in self.achievements.values():
            achievement.rejoined(player)

    def start(self):
        assert not self.started
        self.started = True
        for achievement in self.achievements.values():
            achievement.onUnlocked.addListener(
                self.manager.achievementUnlocked)
            achievement.start()

    def stop(self):
        assert not self.stopped
        self.stopped = True
        for achievement in self.achievements.values():
            achievement.stop()
            achievement.onUnlocked.removeListener(
                self.manager.achievementUnlocked)

    def saveProgress(self, force=False):
        if self.savingProgress and not force:
            return
        if self.player.user is None:
            return

        @dbqueue.add
        @defer.inlineCallbacks
        def saveAchievementProgressToDB():
            self.savingProgress = True
            try:
                for achievement in self.achievements.values():
                    achievement.save()
                    yield dbqueue.wait()
            finally:
                self.savingProgress = False

    def __str__(self):
        return str(self.achievements.values)


class AchievementManager(object):
    SAVE_PERIOD = 20

    achievementDefs = availableAchievements

    def __init__(self, game):
        self.game = game
        self.world = world = game.world
        self.lastSave = timeNow()

        # All players recorded this game, indexed by user id.
        self.allPlayers = {}

        defs = self.achievementDefs
        self.oncePerGameAchievements = [c(world) for c in defs.oncePerGame]
        self.oncePerTeamPerGameAchievements = [
            c(world, team)
            for c in defs.oncePerTeamPerGame
            for team in world.teams
        ]

        self.loop = WeakLoopingCall(self, 'save')
        self.started = False
        self.stopped = False

    def save(self, force=False):
        for playerAchievements in list(self.allPlayers.values()):
            playerAchievements.saveProgress(force=force)

    def start(self):
        assert not self.started
        self.started = True
        for player in self.world.players:
            self.playerAdded(player)

        self.world.onPlayerAdded.addListener(self.playerAdded)
        self.loop.start(self.SAVE_PERIOD)

        for a in self.oncePerGameAchievements:
            a.onUnlocked.addListener(self.achievementUnlocked)
            a.start()
        for a in self.oncePerTeamPerGameAchievements:
            a.start()
            a.onUnlocked.addListener(self.achievementUnlocked)

    def stop(self):
        assert not self.stopped
        self.stopped = True
        self.loop.stop()
        self.world.onPlayerAdded.removeListener(self.playerAdded)
        self.save(force=True)
        for a in self.oncePerGameAchievements:
            a.stop()
            a.onUnlocked.removeListener(self.achievementUnlocked)
        for a in self.oncePerTeamPerGameAchievements:
            a.stop()
            a.onUnlocked.removeListener(self.achievementUnlocked)
        for p in list(self.allPlayers.values()):
            p.stop()

    @defer.inlineCallbacks
    def playerAdded(self, player):
        if self.world.isServer and not player.joinComplete:
            # We want to identify by user rather than nickname if the user
            # is authenticated.
            yield player.onJoinComplete.wait()

        name = player.identifyingName
        if name not in self.allPlayers:
            a = PlayerAchievements(self, player)
            self.allPlayers[name] = a
            a.start()
        else:
            self.allPlayers[name].rejoined(player)

    def triggerAchievement(self, player, achievementId):
        '''
        Called from stats manager to trigger a stats-related achievement.
        Never raises an exception.
        '''
        try:
            a = self.allPlayers[player.identifyingName].achievements[achievementId]
            a.achievementTriggered()
        except Exception:
            log.exception('Error triggering achievement')

    def achievementUnlocked(self, achievement, player):
        if player.user is not None:
            player.user.achievementUnlocked(achievement.idstring)
        self.game.sendServerCommand(
            AchievementUnlockedMsg(player.id, achievement.idstring))
