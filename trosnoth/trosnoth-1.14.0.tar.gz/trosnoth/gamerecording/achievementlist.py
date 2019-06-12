from collections import defaultdict
import logging

import simplejson
from twisted.internet import reactor

from trosnoth.const import (
    SHOT_HIT, GRENADE_HIT, SHOXWAVE_HIT,
    ACHIEVEMENT_TACTICAL, ACHIEVEMENT_TERRITORY, ACHIEVEMENT_AFTER_GAME,
)
from trosnoth.model.upgrades import allUpgrades
from trosnoth.model.zone import ZoneState
from trosnoth.utils.event import Event
from trosnoth.utils.lifespan import LifeSpan

log = logging.getLogger(__name__)


##################################
# Collection of all achievements #
##################################

class AchievementSet(object):
    def __init__(self, template=None):
        self.all = []
        self.byId = {}
        self.oncePerGame = []
        self.oncePerTeamPerGame = []
        self.perPlayer = []
        if template:
            for achievement in template.all:
                self.register(achievement)

    def getAchievementDetails(self, idstring):
        if isinstance(idstring, str):
            idstring = idstring.encode('Latin-1')
        achievement = self.byId[idstring]
        if achievement.name == '':
            return idstring, achievement.description
        else:
            return achievement.name, achievement.description

    def register(self, achievement):
        if achievement.idstring in self.byId:
            raise KeyError('achievement with id %r already registered' % (
                    achievement.idstring,))

        self.all.append(achievement)
        self.byId[achievement.idstring] = achievement

        if achievement.oncePerGame:
            self.oncePerGame.append(achievement)
        elif achievement.oncePerTeamPerGame:
            self.oncePerTeamPerGame.append(achievement)
        else:
            assert achievement.perPlayer
            self.perPlayer.append(achievement)
        return achievement

availableAchievements = AchievementSet()


############################
# Achievement base classes #
############################

class Achievement(object):

    keepProgress = False
    categories = {ACHIEVEMENT_TACTICAL}

    oncePerGame = False
    oncePerTeamPerGame = False

    def __init__(self, world):
        self.world = world
        self.unlocked = False
        self.registered = False
        self.onUnlocked = Event()
        self.lifespan = LifeSpan()

    def save(self):
        return False

    def start(self):
        if self.isActive():
            self.register()

    def stop(self):
        self.lifespan.stop()
        if self.registered:
            self.unregister()

    def register(self):
        self.registered = True

    def unregister(self):
        self.registered = False

    def _sendUnlocked(self, player):
        self.onUnlocked(self, player)
        log.debug(self.achievementString(player))

    def achievementString(self, player):
        return 'Achievement unlocked by %s! - %s' % (
            player.nick, self.name if self.name else self.idstring)

    def __str__(self):
        return '%s' % self.idstring

    @classmethod
    def describe(cls):
        '''
        Used when saving achievement meta-information to file. Should be
        overwritten by higher level classes.
        '''
        information = {'name': cls.name,
                       'description': cls.description,
                       'type': 'boolean'}
        return {cls.idstring: information}

    def isActive(self):
        return not self.unlocked


class PlayerAchievement(Achievement):
    perPlayer = True

    def __init__(self, player, world, *args, **kwargs):
        super(PlayerAchievement, self).__init__(world, *args, **kwargs)
        self.player = player
        self.world = world

    def rejoined(self, player):
        if self.registered:
            self.unregister()
            self.player = player
            self.register()
        else:
            self.player = player

    def achievementTriggered(self):
        if not (self.categories & self.world.activeAchievementCategories):
            return

        self.unlocked = True
        self._sendUnlocked(self.player)
        if self.registered and not self.isActive():
            self.unregister()


class PlayerlessAchievement(Achievement):
    perPlayer = False

    def achievementTriggeredFor(self, players):
        if self.unlocked:
            return
        if not (self.categories & self.world.activeAchievementCategories):
            return

        self.unlocked = True
        for player in players:
            self._sendUnlocked(player)
        if self.registered and not self.isActive():
            self.unregister()

    def isActive(self):
        # By default, there's no need to stay subscribed to events once the
        # achievement is achieved.
        return not self.unlocked


class OncePerGame(PlayerlessAchievement):
    oncePerGame = True


class OncePerTeamPerGame(PlayerlessAchievement):
    oncePerTeamPerGame = True

    def __init__(self, world, team, *args, **kwargs):
        super(OncePerTeamPerGame, self).__init__(world, *args, **kwargs)
        self.team = team


class OncePerPlayerPerGame(PlayerAchievement):
    def achievementTriggered(self):
        if not self.unlocked:
            super(OncePerPlayerPerGame, self).achievementTriggered()


class NoLimit(PlayerAchievement):
    def isActive(self):
        return True


class OnceEverPerPlayer(PlayerAchievement):
    '''
    self.unlocked is "unlocked this time".
    self.previouslyUnlocked is "unlocked previously".
    '''
    keepProgress = True

    def __init__(self, *args, **kwargs):
        super(OnceEverPerPlayer, self).__init__(*args, **kwargs)
        self.previouslyUnlocked = False
        self.dbObject = None
        self.previouslyUnlocked = False
        self.progress = 0
        self.data = None

        if self.player is not None and not self.player.bot:
            # Delay this call so that the auth user can be set
            reactor.callLater(0, self.readExistingData)

    def save(self):
        if self.dbObject is None:
            return False
        if self.progress != self.dbObject.progress:
            self.dbObject.progress = self.progress
            self.dbObject.unlocked = self.unlocked or self.previouslyUnlocked
            self.dbObject.save()
            return True
        return False

    def readExistingData(self):
        user = self.player.user
        if user is None:
            return

        self.dbObject = record = user.getAchievementRecord(self.idstring)
        if record.data:
            self.data = simplejson.loads(record.data)
        else:
            self.data = None
        self.previouslyUnlocked = record.unlocked
        self.progress = record.progress

    def achievementTriggered(self):
        if not self.unlocked and not self.previouslyUnlocked:
            super(OnceEverPerPlayer, self).achievementTriggered()

    def isActive(self):
        return not self.unlocked and not self.previouslyUnlocked


###################
# Streak subclass #
###################

class Streak(PlayerAchievement):
    streakTarget = -1

    def __init__(self, *args, **kwargs):
        self.progress = 0
        super(Streak, self).__init__(*args, **kwargs)

    def increment(self, amount=1):
        if not (self.categories & self.world.activeAchievementCategories):
            return
        self.progress = min(self.streakTarget, self.progress + amount)

        if self.progress == self.streakTarget:
            self.achievementTriggered()

    def reset(self):
        self.progress = 0

    def __str__(self):
        return '%s: %d/%d' % (
            self.idstring, self.progress, self.streakTarget)

    @classmethod
    def describe(self):
        information = {'name': self.name,
                       'description': self.description,
                       'type': 'incremental',
                       'requirements': self.streakTarget,
                       'keepProgress': self.keepProgress}
        return {self.idstring: information}


##########################
# Achievement subclasses #
##########################

class ChecklistAchievement(Achievement):
    requiredItems = set()

    def __init__(self, *args, **kwargs):
        super(ChecklistAchievement, self).__init__(*args, **kwargs)

    def addItem(self, item):
        if not (self.categories & self.world.activeAchievementCategories):
            return
        if not self.data:
            self.data = set()
        self.data.add(item)

        if self.requiredItems == self.data:
            self.achievementTriggered()

    def __str__(self):
        return '%s: %d/%d items' % (self.idstring, len(self.data),
                len(self.requiredItems))

    @classmethod
    def describe(self):
        information = {'name': self.name,
                       'description': self.description,
                       'type': 'checklist',
                       'requirements': list(self.requiredItems),
                       'keepProgress': self.keepProgress}
        return {self.idstring: information}


class PersistedChecklistAchievement(ChecklistAchievement, OnceEverPerPlayer):
    def save(self):
        if self.dbObject is None:
            return False
        changed = False
        if self.progress != self.dbObject.progress:
            self.dbObject.progress = self.progress
            changed = True

        data = simplejson.dumps(list(self.data))
        if data != self.dbObject.data:
            self.dbObject.data = data
            changed = True

        if changed:
            self.dbObject.unlocked = self.unlocked or self.previouslyUnlocked
            self.dbObject.save()

        return changed

    def readExistingData(self):
        super(PersistedChecklistAchievement, self).readExistingData()
        self.data = set(self.data or [])


class TimedAchievement(PlayerAchievement):
    requiredValue = -1
    timeWindow = -1

    def __init__(self, *args, **kwargs):
        super(TimedAchievement, self).__init__(*args, **kwargs)
        self.rollingList = []

    def addToList(self):
        now = self.world.getMonotonicTime()
        self.rollingList.append(now)

        while (self.rollingList and (
                now - self.rollingList[0]) > self.timeWindow):
            del self.rollingList[0]

        if len(self.rollingList) >= self.requiredValue:
            self.achievementTriggered()
            self.rollingList = []


#########################
# Concrete Achievements #
#########################

@availableAchievements.register
class Neutraliser(NoLimit):
    idstring = b'neutraliser'
    name = 'Neutraliser'
    description = 'Neutralise three zones with a single tag'
    categories = {ACHIEVEMENT_TERRITORY}

    def register(self):
        super(Neutraliser, self).register()
        self.player.onNeutralisedSector.addListener(
            self.neutralisedSector, lifespan=self.lifespan)

    def neutralisedSector(self, zoneCount):
        if zoneCount >= 3:
            self.achievementTriggered()


class MultiTagBase(Streak, OncePerPlayerPerGame):
    categories = {ACHIEVEMENT_TERRITORY}
    def register(self):
        super(MultiTagBase, self).register()
        self.player.onTaggedZone.addListener(
            self.taggedZone, lifespan=self.lifespan)
        self.player.onDied.addListener(self.died, lifespan=self.lifespan)

    def taggedZone(self, *args, **kwargs):
        self.increment()

    def died(self, *args, **kwargs):
        self.reset()


@availableAchievements.register
class MultiTagSmall(MultiTagBase):
    idstring = b'multiTagSmall'
    name = "I Ain't Even Winded"
    description = 'Capture three zones in a single life'
    streakTarget = 3


@availableAchievements.register
class MultiTagMedium(MultiTagBase):
    idstring = b'multiTagMedium'
    name = 'The Long Way Home'
    description = 'Capture five zones in a single life'
    streakTarget = 5


@availableAchievements.register
class MultiTagLarge(MultiTagBase):
    idstring = b'multiTagLarge'
    name = 'Cross-Country Marathon'
    description = 'Capture eight zones in a single life'
    streakTarget = 8


@availableAchievements.register
class Janitor(Streak, OncePerPlayerPerGame):
    idstring = b'neutralCapturesMedium'
    name = 'Janitor'
    description = (
        'Capture 5 neutral zones away from enemy territory in a single game')
    streakTarget = 5
    categories = {ACHIEVEMENT_TERRITORY}

    def register(self):
        super(Janitor, self).register()
        self.player.onTaggedZone.addListener(
            self.taggedZone, lifespan=self.lifespan)

    def taggedZone(self, zone, previousOwner):
        if previousOwner is None and not any(
                self.player.isEnemyTeam(z.owner)
                for z in zone.getAdjacentZones()):
            self.increment()


class TotalTagsBase(Streak, OnceEverPerPlayer):
    categories = {ACHIEVEMENT_TERRITORY}

    def register(self):
        super(TotalTagsBase, self).register()
        self.player.onTaggedZone.addListener(
            self.taggedZone, lifespan=self.lifespan)

    def taggedZone(self, *args, **kwargs):
        self.increment()


@availableAchievements.register
class TotalTagsSmall(TotalTagsBase):
    idstring = b'totalTagsSmall'
    name = 'Cultural Assimilation'
    description = 'Capture 20 zones'
    streakTarget = 20


@availableAchievements.register
class TotalTagsMedium(TotalTagsBase):
    idstring = b'totalTagsMedium'
    name = 'Globalization'
    description = 'Capture 50 zones'
    streakTarget = 50


class MultiKillBase(Streak, OncePerPlayerPerGame):
    def register(self):
        super(MultiKillBase, self).register()
        self.player.onKilled.addListener(
            self.killedPlayer, lifespan=self.lifespan)
        self.player.onDied.addListener(self.died, lifespan=self.lifespan)

    def killedPlayer(self, *args, **kwargs):
        self.increment()

    def died(self, *args, **kwargs):
        self.reset()


@availableAchievements.register
class MultiKillSmall(MultiKillBase):
    idstring = b'multikillSmall'
    name = 'Triple Threat'
    description = 'Kill three enemies in a single life'
    streakTarget = 3


@availableAchievements.register
class MultiKillMedium(MultiKillBase):
    idstring = b'multikillMedium'
    name = 'High Five'
    description = 'Kill five enemies in a single life'
    streakTarget = 5


@availableAchievements.register
class MultiKillLarge(MultiKillBase):
    idstring = b'multikillLarge'
    name = "That's the Badger"
    description = 'Kill nine enemies in a single life'
    streakTarget = 9


class TotalKillsBase(Streak, OnceEverPerPlayer):
    def register(self):
        super(TotalKillsBase, self).register()
        self.player.onKilled.addListener(
            self.killedPlayer, lifespan=self.lifespan)

    def killedPlayer(self, *args, **kwargs):
        self.increment()


@availableAchievements.register
class TotalKillsSmall(TotalKillsBase):
    idstring = b'totalKillsSmall'
    name = 'Family Friendly Fun'
    description = 'Kill 50 enemies'
    streakTarget = 50


@availableAchievements.register
class TotalKillsMedium(TotalKillsBase):
    idstring = b'totalKillsMedium'
    name = "All in a Day's Work"
    description = 'Kill 100 enemies'
    streakTarget = 100


@availableAchievements.register
class ShoppingSpree(Streak, OncePerPlayerPerGame):
    idstring = b'multiUpgradesSmall'
    name =  'Shopping Spree'
    description = 'Buy two upgrades in a single life'
    streakTarget = 2

    def register(self):
        super(ShoppingSpree, self).register()
        self.player.onUsedUpgrade.addListener(
            self.usedUpgrade, lifespan=self.lifespan)
        self.player.onDied.addListener(self.died, lifespan=self.lifespan)

    def usedUpgrade(self, *args, **kwargs):
        self.increment()

    def died(self, *args, **kwargs):
        self.reset()


@availableAchievements.register
class SmartShopper(Streak, OncePerPlayerPerGame):
    idstring = b'multiUpgradesMedium'
    name = 'Smart Shopper'
    description = 'Buy five upgrades in a single game'
    streakTarget = 5

    def register(self):
        super(SmartShopper, self).register()
        self.player.onUsedUpgrade.addListener(
            self.usedUpgrade, lifespan=self.lifespan)

    def usedUpgrade(self, *args, **kwargs):
        self.increment()


@availableAchievements.register
class BulletsSmall(Streak, OncePerPlayerPerGame):
    idstring = b'bulletsSmall'
    name = 'Machine Gunner'
    description = 'Shoot 100 bullets in a single life'
    streakTarget = 100

    def register(self):
        super(BulletsSmall, self).register()
        self.player.onShotFired.addListener(
            self.shotFired, lifespan=self.lifespan)
        self.player.onDied.addListener(self.died, lifespan=self.lifespan)

    def shotFired(self, *args, **kwargs):
        self.increment()

    def died(self, *args, **kwargs):
        self.reset()


@availableAchievements.register
class BulletsMedium(Streak, OncePerPlayerPerGame):
    idstring = b'bulletsMedium'
    name = 'Ammunition Overdrive'
    description = 'Shoot 500 bullets in a single game'
    streakTarget = 500

    def register(self):
        super(BulletsMedium, self).register()
        self.player.onShotFired.addListener(
            self.shotFired, lifespan=self.lifespan)

    def shotFired(self, *args, **kwargs):
        self.increment()


class WinnerBase(Streak, OnceEverPerPlayer):
    def register(self):
        super(WinnerBase, self).register()
        self.world.onStandardGameFinished.addListener(
            self.gameOver, lifespan=self.lifespan)

    def gameOver(self, team, *args, **kwarsg):
        if not self.player.isFriendsWithTeam(team):
            return

        playerCount = sum(1 for p in self.world.players if not p.bot)
        if playerCount >= 6:
            self.increment()


@availableAchievements.register
class WinnerTiny(WinnerBase):
    idstring = b'winnerTiny'
    name = 'Trosnoth Newbie'
    description = 'Win your first game of Trosnoth (minimum 6 players)'
    streakTarget = 1


@availableAchievements.register
class WinnerSmall(WinnerBase):
    idstring = b'winnerSmall'
    name = 'Trosnoth Amateur'
    description = 'Win 5 games of Trosnoth (minimum 6 players)'
    streakTarget = 5


@availableAchievements.register
class WinnerMedium(WinnerBase):
    idstring = b'winnerMedium'
    name = 'Trosnoth Consultant'
    description = 'Win 10 games of Trosnoth (minimum 6 players)'
    streakTarget = 10


@availableAchievements.register
class WinnerLarge(WinnerBase):
    idstring = b'winnerLarge'
    name = 'Trosnoth Professional'
    description = 'Win 20 games of Trosnoth (minimum 6 players)'
    streakTarget = 20


@availableAchievements.register
class WinnerHuge(WinnerBase):
    idstring = b'winnerHuge'
    name = 'Trosnoth Expert'
    description = 'Win 50 games of Trosnoth (minimum 6 players)'
    streakTarget = 50


@availableAchievements.register
class AssistTags(Streak, OncePerPlayerPerGame):
    idstring = b'assistTags'
    name = 'Credit to Team'
    description = 'Assist in the tagging of five zones in a single game'
    streakTarget = 5
    categories = {ACHIEVEMENT_TERRITORY}

    def register(self):
        super(AssistTags, self).register()
        self.world.onZoneTagged.addListener(
            self.zoneTagged, lifespan=self.lifespan)

    def zoneTagged(self, zone, player, *args, **kwargs):
        if player and self.player.isFriendsWith(player):
            if player == self.player:
                return
            if self.player in zone.players and not self.player.dead:
                self.increment()


class QuickKillBase(TimedAchievement):
    deathTypes = b''

    def register(self):
        super(QuickKillBase, self).register()
        self.player.onKilled.addListener(
            self.killedPlayer, lifespan=self.lifespan)

    def killedPlayer(self, target, deathType, *args, **kwargs):
        if deathType in self.deathTypes:
            self.addToList()


@availableAchievements.register
class QuickKillSmall(QuickKillBase, NoLimit):
    requiredValue = 2
    timeWindow = 5
    deathTypes = {SHOT_HIT, SHOXWAVE_HIT}
    idstring = b'quickKillSmall'
    name = 'Double Kill'
    description = 'Kill two enemies within five seconds (no grenades)'


@availableAchievements.register
class QuickKillMedium(QuickKillBase, NoLimit):
    requiredValue = 3
    timeWindow = 5
    deathTypes = {SHOT_HIT, SHOXWAVE_HIT}
    idstring = b'quickKillMedium'
    name = 'Triple Kill'
    description = 'Kill three enemies within five seconds (no grenades)'


@availableAchievements.register
class GrenadeMultiKill(QuickKillBase, NoLimit):
    requiredValue = 3
    # Processing of achievements should happen within 0.25 secs
    timeWindow = 0.25
    deathTypes = {GRENADE_HIT}
    idstring = b'grenadeMultikill'
    name = "It's Super Effective!"
    description = 'Kill three enemies with a single grenade'


@availableAchievements.register
class RicochetAchievement(OncePerPlayerPerGame):
    name = 'Bouncy Flag'
    description = (
        'Kill an enemy with a bullet that has ricocheted at least once')
    idstring = b'ricochetKill'

    def register(self):
        super(RicochetAchievement, self).register()
        self.player.onShotHurtPlayer.addListener(
            self.hurtPlayer, lifespan=self.lifespan)

    def hurtPlayer(self, target, shot, *args, **kwargs):
        if target.dead and shot.hasBounced:
            self.achievementTriggered()


@availableAchievements.register
class AccuracySmall(OncePerPlayerPerGame):
    name = 'Boom, Headshot'
    description = 'Have an accuracy of 10% or higher during a game'
    idstring = b'accuracySmall'


@availableAchievements.register
class AccuracyMedium(OncePerPlayerPerGame):
    name = "Sniping's a Good Job, Mate"
    description = 'Have an accuracy of 15% or higher during a game'
    idstring = b'accuracyMedium'


@availableAchievements.register
class AccuracyLarge(OncePerPlayerPerGame):
    name = 'Professionals Have Standards'
    description = 'Have an accuracy of 20% or higher during a game'
    idstring = b'accuracyLarge'


@availableAchievements.register
class TotalAliveTime(OnceEverPerPlayer):
    name = 'Long Live the King'
    description = 'Rack up a total of 1000 seconds of alive time'
    idstring = b'totalAliveTime'


@availableAchievements.register
class StayingAlive(OncePerPlayerPerGame):
    name = 'Never Asleep on the Job'
    description = 'Be alive at least 75% of the time'
    idstring = b'stayingAlive'


@availableAchievements.register
class AliveStreak(OncePerPlayerPerGame):
    name = 'Still Alive'
    description = 'Stay alive for at least 180 seconds in a single life'
    idstring = b'aliveStreak'


@availableAchievements.register
class UseCoinsEfficiently(OncePerPlayerPerGame):
    name = 'Waste Not, Want Not'
    description = ('Use or contribute at least 50% of the coins you earn '
            'during a game')
    idstring = b'useCoinsEfficiently'


@availableAchievements.register
class LongRangeKill(OncePerPlayerPerGame):
    name = 'Long-Range Ballistics'
    description = 'Hit an enemy at the maximum range of your gun'
    idstring = b'longRangeKill'

    def register(self):
        super(LongRangeKill, self).register()
        self.player.onShotHurtPlayer.addListener(
            self.hurtPlayer, lifespan=self.lifespan)

    def hurtPlayer(self, target, shot):
        if shot.timeLeft < 0.1:
            self.achievementTriggered()


@availableAchievements.register
class TagsAndKills(OncePerPlayerPerGame):
    name = 'All-Rounder'
    description = 'Kill 10 people and tag 5 zones in a single life'
    idstring = b'tagsAndKills'
    categories = {ACHIEVEMENT_TERRITORY}

    requiredTags = 5
    requiredKills = 10

    def __init__(self, *args, **kwargs):
        super(TagsAndKills, self).__init__(*args, **kwargs)
        self.tags = 0
        self.kills = 0

    def register(self):
        super(TagsAndKills, self).register()
        self.player.onTaggedZone.addListener(
            self.taggedZone, lifespan=self.lifespan)
        self.player.onKilled.addListener(
            self.killedPlayer, lifespan=self.lifespan)
        self.player.onDied.addListener(self.died, lifespan=self.lifespan)

    def taggedZone(self, *args, **kwargs):
        self.tags = min(self.tags + 1, self.requiredTags)
        self.checkTrigger()

    def killedPlayer(self, *args, **kwargs):
        self.kills = min(self.kills + 1, self.requiredKills)
        self.checkTrigger()

    def checkTrigger(self):
        if self.kills == self.requiredKills and self.tags == self.requiredTags:
            self.achievementTriggered()

    def died(self, *args, **kwargs):
        self.kills = 0
        self.tags = 0


@availableAchievements.register
class KillEnemyWithCoins(OncePerPlayerPerGame):
    name = 'Stop Right There, Criminal Scum'
    description = 'Kill an enemy holding $600 or more'
    idstring = b'killEnemyWithCoins'

    def register(self):
        super(KillEnemyWithCoins, self).register()
        self.player.onKilled.addListener(
            self.killedPlayer, lifespan=self.lifespan)

    def killedPlayer(self, target, *args, **kwargs):
        if target.coins >= 600:
            self.achievementTriggered()


@availableAchievements.register
class DestroyCoins(Streak, OnceEverPerPlayer):
    idstring = b'destroyCoins'
    name = 'The Recession we Had to Have'
    description = 'Destroy $5000 by killing the players carrying them'
    streakTarget = 5000

    def register(self):
        super(DestroyCoins, self).register()
        self.player.onKilled.addListener(
            self.killedPlayer, lifespan=self.lifespan)

    def killedPlayer(self, target, *args, **kwargs):
        self.increment(target.coins)


@availableAchievements.register
class EarnCoins(Streak, OnceEverPerPlayer):
    idstring = b'earnCoins'
    name = 'Stimulus Package'
    description = 'Earn $5000'
    streakTarget = 5000

    def __init__(self, *args, **kwargs):
        super(EarnCoins, self).__init__(*args, **kwargs)
        self.lastCoins = self.player.coins

    def register(self):
        super(EarnCoins, self).register()
        self.player.onCoinsChanged.addListener(
            self.coinsChanged, lifespan=self.lifespan)

    def coinsChanged(self, *args, **kwargs):
        if self.player.coins > self.lastCoins:
            self.increment(self.player.coins - self.lastCoins)
        self.lastCoins = self.player.coins


@availableAchievements.register
class BuyEveryUpgrade(PersistedChecklistAchievement):
    idstring = b'buyEveryUpgrade'
    name = 'Technology Whiz'
    description = 'Use every upgrade at least once'
    requiredItems = set(u.upgradeType for u in allUpgrades)

    def register(self):
        super(BuyEveryUpgrade, self).register()
        self.player.onUsedUpgrade.addListener(
            self.usedUpgrade, lifespan=self.lifespan)

    def usedUpgrade(self, upgrade, *args, **kwargs):
        self.addItem(upgrade.upgradeType)


@availableAchievements.register
class UseMinimapDisruption(OncePerPlayerPerGame):
    idstring = b'minimapDisruption'
    name = 'The Rader Appears to be... Jammed!'
    description = 'Use a minimap disruption'

    def register(self):
        super(UseMinimapDisruption, self).register()
        self.player.onUsedUpgrade.addListener(
            self.usedUpgrade, lifespan=self.lifespan)

    def usedUpgrade(self, upgrade, *args, **kwargs):
        if upgrade.upgradeType == b'm':
            self.achievementTriggered()


@availableAchievements.register
class GoodManners(OncePerPlayerPerGame):
    idstring = b'goodManners'
    name = 'Good Manners'
    description = 'Say "gg" after the game finishes'
    categories = {ACHIEVEMENT_AFTER_GAME}

    def register(self):
        super(GoodManners, self).register()
        self.world.onOpenChatReceived.addListener(
            self.chat, lifespan=self.lifespan)

    def chat(self, text, sender, *args, **kwargs):
        if text.lower().strip() == 'gg' and sender == self.player:
            self.achievementTriggered()


@availableAchievements.register
class DarkZoneKills(Streak, OncePerPlayerPerGame):
    idstring = b'darkZoneKills'
    name = 'Behind Enemy Lines'
    description = "Kill five enemies when you're in a dark zone of their colour"
    streakTarget = 5

    def register(self):
        super(DarkZoneKills, self).register()
        self.player.onKilled.addListener(
            self.killedPlayer, lifespan=self.lifespan)

    def killedPlayer(self, *args, **kwargs):
        if self.player.team is None:
            return
        zone = self.player.getZone()
        if not zone:
            return
        if (self.player.isEnemyTeam(zone.owner) and zone.dark
                and not self.player.dead):
            self.increment()


class UpgradeKillBase(OncePerPlayerPerGame):
    def register(self):
        super(UpgradeKillBase, self).register()
        self.player.onKilled.addListener(
            self.killedPlayer, lifespan=self.lifespan)

    def killedPlayer(
            self, target, deathType, hadItems=None, *args, **kwargs):
        if any(item.upgradeType in self.upgradeTypes for item in hadItems):
            self.achievementTriggered()


@availableAchievements.register
class NinjaKill(UpgradeKillBase):
    idstring = b'ninjaKill'
    name = "Ninjas Can't Catch You if You're on Fire"
    description = 'Kill an invisible ninja'
    upgradeTypes = b'n'


@availableAchievements.register
class AntiDisruption(UpgradeKillBase):
    idstring = b'antiDisruption'
    name = "Back Online"
    description = 'Kill an enemy who is using a Minimap Disruption'
    upgradeTypes = b'm'


@availableAchievements.register
class MinimapDisruptionTag(OncePerPlayerPerGame):
    name = 'Under the Radar'
    description = 'Tag a zone while the enemy\'s minimap is disrupted'
    idstring = b'disruptionTag'
    categories = {ACHIEVEMENT_TERRITORY}

    def register(self):
        super(MinimapDisruptionTag, self).register()
        self.player.onTaggedZone.addListener(
            self.taggedZone, lifespan=self.lifespan)

    def taggedZone(self, *args, **kwargs):
        if self.player.team and self.player.team.usingMinimapDisruption:
            self.achievementTriggered()


@availableAchievements.register
class ChokepointSpam(Streak, OncePerPlayerPerGame):
    idstring = b'chokepointSpam'
    name = "Chokepoint Checkmate"
    description = 'Kill three players without moving or dying (no upgrades)'
    streakTarget = 3

    pos = (0, 0)

    def register(self):
        super(ChokepointSpam, self).register()
        self.player.onKilled.addListener(
            self.killedPlayer, lifespan=self.lifespan)
        self.player.onShotFired.addListener(
            self.shotFired, lifespan=self.lifespan)

    def shotFired(self, *args, **kwargs):
        # Strictly speaking, the player is still able to move or die, but if
        # they don't shoot from exactly the same spot it won't count anyway.
        if self.player.pos != self.pos:
            self.reset()
        self.pos = self.player.pos

    def killedPlayer(self, shooter, deathType, *args, **kwargs):
        if not self.player.items.hasAny() and deathType != GRENADE_HIT:
            self.increment()


@availableAchievements.register
class KillAsRabbit(OncePerPlayerPerGame):
    name = 'Never Surrender'
    description = 'Kill an enemy after losing a game'
    idstring = b'killAsRabbit'
    categories = {ACHIEVEMENT_AFTER_GAME}

    def register(self):
        super(KillAsRabbit, self).register()
        self.player.onKilled.addListener(
            self.killedPlayer, lifespan=self.lifespan)

    def killedPlayer(self, *args, **kwargs):
        if self.world.uiOptions.showGameOver:
            winningTeam = self.world.uiOptions.winningTeam
            if (self.player.team is not None and
                    self.player.isEnemyTeam(winningTeam)):
                self.achievementTriggered()


@availableAchievements.register
class RabbitKill(OncePerPlayerPerGame):
    name = 'Icing on the Cake'
    description = 'Kill an enemy after winning a game'
    idstring = b'killRabbit'
    categories = {ACHIEVEMENT_AFTER_GAME}

    def register(self):
        super(RabbitKill, self).register()
        self.player.onKilled.addListener(
            self.killedPlayer, lifespan=self.lifespan)

    def killedPlayer(self, target, *args, **kwargs):
        if self.world.uiOptions.showGameOver:
            winningTeam = self.world.uiOptions.winningTeam
            if (winningTeam == self.player.team and
                    self.player.isEnemyTeam(target.team)):
                self.achievementTriggered()


@availableAchievements.register
class RabbitSurvival(OncePerPlayerPerGame):
    name = 'Catch Me If You Can'
    description = 'Survive as a rabbit to the end of the hunt'
    idstring = b'rabbitSurvival'
    categories = {ACHIEVEMENT_AFTER_GAME}


@availableAchievements.register
class EveryoneDied(OncePerGame):
    idstring = b'everyoneDied'
    name = 'We All Fall Down'
    description = (
        'Be dead at the same time as everyone else in a game of 6 or more '
        'players')

    def register(self):
        super(EveryoneDied, self).register()
        self.world.onPlayerKill.addListener(
            self.playerKilled, lifespan=self.lifespan)

    def playerKilled(self, killer, *args, **kwargs):
        if len(self.world.players) >= 6:
            if all(p.dead for p in self.world.players):
                self.achievementTriggeredFor(self.world.players)


@availableAchievements.register
class FirstKill(OncePerGame):
    name = 'First Blood'
    description = 'Make the first kill of the game'
    idstring = b'firstKill'

    def register(self):
        super(FirstKill, self).register()
        self.world.onPlayerKill.addListener(
            self.playerKilled, lifespan=self.lifespan)

    def playerKilled(self, killer, *args, **kwargs):
        if killer:
            self.achievementTriggeredFor({killer})


@availableAchievements.register
class FirstTag(OncePerGame):
    name = 'Game On'
    description = 'Tag or assist in the tagging of the first zone in a game'
    idstring = b'firstTag'
    categories = {ACHIEVEMENT_TERRITORY}

    def register(self):
        super(FirstTag, self).register()
        self.world.onZoneTagged.addListener(
            self.zoneTagged, lifespan=self.lifespan)

    def zoneTagged(self, zone, player, *args, **kwargs):
        if not player:
            return
        team = player.team
        helpers = {p for p in zone.players if p.team == team and not p.dead}
        self.achievementTriggeredFor(helpers)


@availableAchievements.register
class FirstRespawn(OncePerGame):
    name = 'Finger on the Trigger'
    description = 'Be the first person to respawn (minimum 6 players)'
    idstring = b'firstRespawn'

    def register(self):
        super(FirstRespawn, self).register()
        self.world.onPlayerRespawn.addListener(
            self.playerRespawned, lifespan=self.lifespan)

    def playerRespawned(self, player, *args, **kwargs):
        if len(self.world.players) < 6:
            self.achievementTriggeredFor([])
        else:
            self.achievementTriggeredFor({player})


@availableAchievements.register
class LastTag(OncePerGame):
    name = 'And the Dirt is Gone'
    description = 'Tag or assist in the tagging of the final zone'
    idstring = b'finalTag'
    categories = {ACHIEVEMENT_TERRITORY, ACHIEVEMENT_AFTER_GAME}

    def register(self):
        super(LastTag, self).register()
        self.world.onZoneTagged.addListener(
            self.zoneTagged, lifespan=self.lifespan)

    def zoneTagged(self, zone, player, *args, **kwargs):
        if not player:
            return
        team = player.team

        if team and team.opposingTeam.numZonesOwned == 0:
            winners = {
                p for p in zone.players
                if p.team == team and not p.dead}
            self.achievementTriggeredFor(winners)


@availableAchievements.register
class LoseWithEntireTeamDead(OncePerGame):
    name = 'Fight to the Death'
    description = 'Lose with entire team dead (minimum 6 players)'
    idstring = b'losingTeamDead'
    categories = {ACHIEVEMENT_TACTICAL, ACHIEVEMENT_AFTER_GAME}

    def register(self):
        super(LoseWithEntireTeamDead, self).register()
        self.world.onZoneTagged.addListener(self.zoneTagged)

    def unregister(self):
        super(LoseWithEntireTeamDead, self).unregister()
        self.world.onZoneTagged.removeListener(self.zoneTagged)

    def zoneTagged(self, zone, player, *args, **kwarsg):
        if not player:
            return
        if len(self.world.players) < 6:
            return
        team = player.team

        if team and team.opposingTeam.numZonesOwned == 0:
            losingTeam = team.opposingTeam
            losers = {p for p in self.world.players if p.team == losingTeam}
            if all(p.dead for p in losers):
                self.achievementTriggeredFor(losers)


@availableAchievements.register
class Domination(OncePerPlayerPerGame):
    name = 'Domination'
    description = 'Kill the same enemy five times in a single game'
    idstring = b'domination'
    streakTarget = 5

    def __init__(self, *args, **kwargs):
        super(Domination, self).__init__(*args, **kwargs)
        self.playerKills = defaultdict(int)

    def register(self):
        super(Domination, self).register()
        self.player.onKilled.addListener(
            self.killedPlayer, lifespan=self.lifespan)

    def killedPlayer(self, target, *args, **kwargs):
        nick = target.identifyingName
        self.playerKills[nick] += 1
        if self.playerKills[nick] == self.streakTarget:
            self.achievementTriggered()


@availableAchievements.register
class MutualKill(NoLimit):
    name = 'Eye for an Eye'
    description = 'Kill an enemy at the same time he kills you'
    idstring = b'mutualKill'

    def __init__(self, *args, **kwargs):
        super(MutualKill, self).__init__(*args, **kwargs)
        # Keep a record of the people we kill. If they kill us while they're
        # dead, achievement unlocked.  Similarly, keep a record of who killed
        # us. If we kill them while we're dead, achievement unlocked.
        self.ourKiller = None
        self.kills = set()

    def register(self):
        super(MutualKill, self).register()
        self.player.onDied.addListener(self.died, lifespan=self.lifespan)
        self.player.onKilled.addListener(
            self.killedPlayer, lifespan=self.lifespan)
        self.world.onPlayerRespawn.addListener(
            self.playerRespawned, lifespan=self.lifespan)

    def died(self, killer, *args, **kwargs):
        if not killer:
            return
        if killer.identifyingName in self.kills:
            self.achievementTriggered()
        else:
            self.ourKiller = killer.identifyingName
        self.kills = set()

    def killedPlayer(self, target, *args, **kwargs):
        if target.identifyingName == self.ourKiller:
            self.achievementTriggered()
        else:
            self.kills.add(target.identifyingName)
        self.ourKiller = None

    def playerRespawned(self, player, *args, **kwargs):
        self.kills.discard(player.identifyingName)
        if player == self.player:
            self.ourKiller = None


@availableAchievements.register
class SnatchedZone(OncePerPlayerPerGame):
    idstring = b'snatched'
    name = 'Snatched from the Jaws'
    # This should not be awarded if the tagging team would have been able to
    # tag anyway
    description = 'Tag a zone just before an enemy was about to respawn in it'
    snatchTime = 0.5
    categories = {ACHIEVEMENT_TERRITORY}

    def register(self):
        super(SnatchedZone, self).register()
        self.player.onTaggedZone.addListener(
            self.taggedZone, lifespan=self.lifespan)

    def taggedZone(self, zone, previousOwner, *args, **kwargs):
        if previousOwner is None:
            return

        almostDefenders = 0
        actualDefenders = 0
        actualAttackers = 0
        for player in zone.players:
            if self.player.isFriendsWith(player):
                if not player.dead:
                    actualAttackers += 1
            elif player.team == previousOwner:
                if player.dead:
                    if player.timeTillRespawn < self.snatchTime:
                        almostDefenders += 1
                else:
                    actualDefenders += 1

        if (not ZoneState.canTag(actualAttackers, actualDefenders +
                almostDefenders)):
            # Couldn't have tagged if we'd been half a second later
            self.achievementTriggered()


@availableAchievements.register
class ShieldRevenge(OncePerPlayerPerGame):
    name = 'Shields Up, Weapons Online'
    description = 'Kill the enemy who shot your shield within ten seconds'
    idstring = b'shieldRevenge'

    timeWindow = 10     # Seconds

    def __init__(self, *args, **kwargs):
        super(ShieldRevenge, self).__init__(*args, **kwargs)
        self.shieldKillers = []

    def register(self):
        super(ShieldRevenge, self).register()
        self.player.onShieldDestroyed.addListener(
            self.shieldDestroyed, lifespan=self.lifespan)
        self.player.onDied.addListener(self.died, lifespan=self.lifespan)
        self.player.onKilled.addListener(
            self.killedPlayer, lifespan=self.lifespan)

    def shieldDestroyed(self, shooter, *args, **kwargs):
        self.shieldKillers.append(
            (self.world.getMonotonicTime(), shooter.identifyingName))

    def died(self, *args, **kwargs):
        self.shieldKillers = []

    def killedPlayer(self, target, *args, **kwargs):
        currentTime = self.world.getMonotonicTime()
        while self.shieldKillers:
            time, attacker = self.shieldKillers[0]
            if currentTime - time > self.timeWindow:
                self.shieldKillers.pop(0)
            else:
                break

        for time, attacker in self.shieldKillers:
            if attacker == target.identifyingName:
                self.achievementTriggered()
                break


@availableAchievements.register
class ShieldThenKill(OncePerPlayerPerGame):
    name = 'Armour-Piercing Bullets'
    description = 'Kill an enemy after destroying their shields'
    idstring = b'destroyShield'

    timeWindow = 10     # Seconds

    def __init__(self, *args, **kwargs):
        super(ShieldThenKill, self).__init__(*args, **kwargs)
        self.shieldsKilled = []

    def register(self):
        super(ShieldThenKill, self).register()
        self.player.onDestroyedShield.addListener(
            self.destroyedShield, lifespan=self.lifespan)
        self.player.onDied.addListener(self.died, lifespan=self.lifespan)
        self.player.onKilled.addListener(
            self.killedPlayer, lifespan=self.lifespan)

    def destroyedShield(self, target, *args, **kwargs):
        self.shieldsKilled.append(
            (self.world.getMonotonicTime(), target.id))

    def died(self, *args, **kwargs):
        self.shieldsKilled = []

    def killedPlayer(self, target, *args, **kwargs):
        currentTime = self.world.getMonotonicTime()
        while self.shieldsKilled:
            time, attacker = self.shieldsKilled[0]
            if currentTime - time > self.timeWindow:
                self.shieldsKilled.pop(0)
            else:
                break

        for time, victim in self.shieldsKilled:
            if victim == target.id:
                self.achievementTriggered()
                break


@availableAchievements.register
class ShieldDefence(OncePerPlayerPerGame):
    name = 'Strategic Deployment'
    description = 'Activate a shield just before being shot'
    idstring = b'shieldDefence'

    timeWindow = 0.2    # seconds
    shieldTime = None

    def register(self):
        super(ShieldDefence, self).register()
        self.player.onUsedUpgrade.addListener(
            self.usedUpgrade, lifespan=self.lifespan)
        self.player.onHitByShot.addListener(
            self.hitByShot, lifespan=self.lifespan)

    def usedUpgrade(self, upgrade, *args, **kwargs):
        if upgrade.upgradeType == b's':
            self.shieldTime = self.world.getMonotonicTime()

    def hitByShot(self, *args, **kwargs):
        if self.shieldTime is not None:
            currentTime = self.world.getMonotonicTime()
            if (currentTime - self.shieldTime) <= self.timeWindow:
                self.achievementTriggered()


@availableAchievements.register
class LastManStanding(OncePerTeamPerGame):
    name = 'Never Give Up'
    description = 'Be the last surviving member of your team'
    idstring = b'surviveLast'
    categories = {ACHIEVEMENT_AFTER_GAME}

    def register(self):
        super(LastManStanding, self).register()
        self.world.onPlayerKill.addListener(
            self.playerKilled, lifespan=self.lifespan)
        self.world.onActiveAchievementCategoriesChanged.addListener(
            self.changedCategories, lifespan=self.lifespan)

    def playerKilled(self, killer, *args, **kwargs):
        if ACHIEVEMENT_AFTER_GAME in self.world.activeAchievementCategories:
            self.check()

    def changedCategories(self, *args, **kwarsg):
        self.check()

    def check(self):
        remaining = None

        for player in self.world.players:
            if player.team == self.team and not player.dead:
                if remaining is None:
                    remaining = player
                else:
                    return
        if remaining:
            self.achievementTriggeredFor([remaining])


##################
# Leader Killing #
##################
leaderAchievements = {
                      'adonal': 'Drum Solo',
                      'dcatch': 'Jerakeen Genocide',
                      'dmenge': "Trolling Ain't Easy",
                      'jbartl': 'The Bigger They Are...',
                      'jowen':  'Zergling Rush',
                      'jredmo': 'Kernel Panic',
                      'khethe': 'Vespene Geyser Exhausted',
                      'kjohns': 'All Your Bass are Belong to Us',
                      'lsharl': 'Knight of Catan',
                      'mbrand': 'How do I shot web?',
                      'mwalla': "School's Out",
                      'shorn':  'Employee of the Month',
                      'tirwin': 'Uncomfortably Energetic',
                      'tryan':  'Nerf Warfare'
                      }

leaderNames =        {'adonal': 'ErbaneOrb',
                      'dcatch': 'Kindred',
                      'dmenge': 'Cricket',
                      'jbartl': 'Hrodga',
                      'jowen':  'Nobody',
                      'jredmo': 'Avatar',
                      'khethe': 'Scarecrow',
                      'kjohns': 'Kain',
                      'lsharl': 'Dr. Strangelove',
                      'mbrand': 'PorridgeLord',
                      'mwalla': 'Jupator',
                      'shorn':  'Clamburger',
                      'tirwin': 'Bundy',
                      'tryan':  'Acne'
                      }

leaderAchievements = additionalLeaders = {} # We are not on camp.


# def getLeaderDescription(name):
#     return 'Kill %s three times' % (leaderNames[name],)


# for username, achievementName in leaderAchievements.iteritems():
#     @availableAchievements.register
#     class LeaderMultiKill(Streak, OnceEverPerPlayer):
#         streakTarget = 3
#         idstring = 'leader' + stripPunctuation(username)
#         name = achievementName
#         description = getLeaderDescription(username)
#         username = username
#
#     def register(self):
#         super(TotalKillsBase, self).register()
#         self.player.onKilled.addListener(
#             self.killedPlayer, lifespan=self.lifespan)
#
#     def killedPlayer(self, *args, **kwargs):
#         def killedSomeone(self, msg):
#             player = self.world.getPlayer(msg.targetId)
#             if player.user is None:
#                 return
#             username = player.user.username
#             if username == self.username:
#                 self.increment()
#
#
# #disabled @availableAchievements.register
# class DeveloperKills(KilledSomeoneAchievement, Streak,
#         OnceEverPerPlayer):
#     idstring = 'developerKills'
#     name = 'Developer Destroyer'
#     description = 'Rack up 10 developer kills'
#     streakTarget = 10
#
#     developers = ('jbartl', 'adonal', 'shorn',
#                   'hrodga', 'erbaneorb', 'clamburger')
#
#     def killedSomeone(self, msg):
#         player = self.world.getPlayer(msg.targetId)
#         if player.user is None:
#             return
#         nick = stripPunctuation(player.user.username).lower()
#         if nick in self.developers:
#             self.increment()

# #disabled @availableAchievements.register
# class KillEveryLeader(KilledSomeoneAchievement, PersistedChecklistAchievement):
#     idstring = 'killEveryLeader'
#     name = 'Leaders vs Campers'
#     description = 'Kill every leader at least once'
#     requiredItems = set(map(stripPunctuation,
#                             map(lower, leaderAchievements.keys()
#                                     + additionalLeaders.keys())))
#
#     def killedSomeone(self, msg):
#         player = self.world.getPlayer(msg.targetId)
#         if player.user is None:
#             return
#         nick = stripPunctuation(player.user.username).lower()
#         if nick in self.requiredItems:
#             self.addItem(nick)
