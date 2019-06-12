# coding: utf-8

from django.contrib.auth.models import User
from django.db import models

from trosnoth import dbqueue
from trosnoth.const import DEFAULT_GAME_PORT, DEFAULT_ELEPHANT_NAME


class TrosnothServerSettings(models.Model):
    serverName = models.TextField(
        'Server name', default='My First Trosnoth Server')
    welcomeText = models.TextField('Welcome html', default=(
        'Congratulations! You have successfully installed your Trosnoth '
        'server. <a href="settings">Click here</a> to configure it.'))
    elephantName = models.TextField(
        'Elephant name', default=DEFAULT_ELEPHANT_NAME,
        help_text='What to call the elephant. Elephant owners must be '
                  'configured directly in the database on the desired '
                  'TrosnothUser.')

    webPort = models.SmallIntegerField(
        'Web server port', default=0,
        help_text='Leave as 0 to automatically select a free port.')
    serverPort = models.SmallIntegerField('Authentication port', default=6787)
    manholePort = models.SmallIntegerField(
        'Debug access port', null=True, blank=True, default=None, help_text=(
            'SSH to this port for a Python shell running inside the '
            'authentication server process. Leave blank to disable.'))
    manholePassword = models.TextField(
        'Debug access password', blank=True,
        help_text='Used for debug access ports on all server processes.')
    trustClientUsernames = models.BooleanField(
        'Trust client usernames', default=False,
        help_text='Removes the need for players to create accounts on this '
                  'server by believing the client when it reports the '
                  'username used to log into the device. This is a security '
                  'vulnerability as a coder could easily configure their '
                  'client to pretend that they are someone else. Only use '
                  'this setting if such an eventuality is low risk and low '
                  'cost. This setting only works if the privacy/sendusername '
                  'setting is enabled in policy.ini on client machines.'
    )

    @staticmethod
    def get():
        rows = TrosnothServerSettings.objects.all()
        if rows.count() == 0:
            result = TrosnothServerSettings()
            result.save()
        else:
            result = rows[0]
        return result

    def __str__(self):
        return 'Trosnoth server settings'

    class Meta:
        verbose_name_plural = 'Trosnoth server settings'
        permissions = (
            ('shutdown_server', 'Can shut down server process'),
        )



class Tournament(models.Model):
    name = models.TextField(default='Tournament')
    showOnHomePage = models.BooleanField(default=True)
    matches = models.ManyToManyField('GameRecord', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-pk']


class TrosnothArena(models.Model):
    name = models.TextField(default='New arena')
    enabled = models.BooleanField(default=True)
    autoStartCountDown = models.IntegerField(
        verbose_name='Automatically start new game after (seconds, negative '
                     'to disable)',
        default=90,
    )
    gamePort = models.IntegerField(
        default=DEFAULT_GAME_PORT, unique=True)
    currentTournament = models.ForeignKey(
        Tournament, on_delete=models.SET_NULL,
        null=True, blank=True, default=None)
    profileSlowCalls = models.BooleanField(
        'Log profiling stats for slow calls',
        default=False,
        help_text='Note that this will decrease performance slightly.'
    )

    def __str__(self):
        if self.enabled:
            return self.name
        return '{} (disabled)'.format(self.name)

    class Meta:
        permissions = (
            ('manage_arena', 'Can edit and manage arenas'),
        )


class TrosnothUser(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True)
    nick = models.TextField(unique=True)
    lastSeen = models.DateTimeField(null=True, blank=True)
    oldPasswordHash = models.BinaryField(default=b'')
    ownsElephant = models.BooleanField(default=False)

    def __str__(self):
        if self.user.username == self.nick.lower():
            return self.nick
        return '{} ({})'.format(self.nick, self.user.username)

    @staticmethod
    def fromUser(**kwargs):
        user = User.objects.get(**kwargs)
        if hasattr(user, 'trosnothuser'):
            result = user.trosnothuser
        elif user.username == 'autoadmin':
            # Special case: autoadmin is not allowed to actually play
            raise User.DoesNotExist('autoadmin is not allowed to play')
        else:
            result = TrosnothUser(user=user, nick=user.username)
            result.save()
        return result

    @property
    def username(self):
        return self.user.username

    def setNick(self, nick):
        @dbqueue.add
        def writeNickToDB():
            user = TrosnothUser.fromUser(username=self.username)
            if nick != user.nick:
                user.nick = nick
                user.save()

    def getAchievementRecord(self, achievementId):
        user = TrosnothUser.fromUser(username=self.username)
        if isinstance(achievementId, bytes):
            achievementId = achievementId.decode('Latin-1')

        try:
            achievement = AchievementProgress.objects.get(
                user=user, achievementId=achievementId)
        except AchievementProgress.DoesNotExist:
            achievement = AchievementProgress(
                user=user, achievementId=achievementId)
            achievement.save()
        return achievement

    def achievementUnlocked(self, achievementId):
        if isinstance(achievementId, bytes):
            achievementId = achievementId.decode('Latin-1')

        @dbqueue.add
        def writeUnlockedAchievementToDB():
            user = TrosnothUser.fromUser(username=self.username)
            try:
                achievement = AchievementProgress.objects.get(
                    user=user, achievementId=achievementId)
            except AchievementProgress.DoesNotExist:
                achievement = AchievementProgress(
                    user=user, achievementId=achievementId)
            if not achievement.unlocked:
                achievement.unlocked = True
                achievement.save()



class AchievementProgress(models.Model):
    user = models.ForeignKey(TrosnothUser, on_delete=models.CASCADE)
    achievementId = models.TextField()
    unlocked = models.BooleanField(default=False)
    progress = models.IntegerField(default=0)
    data = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Achievement progress records'
        unique_together = ('user', 'achievementId')

    def __str__(self):
        return '{}: {}'.format(self.user.nick, self.achievementId)


class GameRecord(models.Model):
    started = models.DateTimeField()
    finished = models.DateTimeField()
    gameSeconds = models.FloatField(default=0)
    serverVersion = models.TextField()
    blueTeamName = models.TextField()
    redTeamName = models.TextField()
    winningTeam = models.CharField(max_length=1, blank=True)
    replayName = models.TextField(default='', blank=True)
    zoneCount = models.IntegerField()
    scenario = models.TextField(default='')
    teamScoresEnabled = models.BooleanField(default=False)
    playerScoresEnabled = models.BooleanField(default=False)
    blueTeamScore = models.FloatField(default=0)
    redTeamScore = models.FloatField(default=0)

    def __str__(self):
        secs = self.gameSeconds
        mins, secs = divmod(secs, 60)
        if mins == 0:
            duration = '{} s'.format(round(secs, 2))
        else:
            duration = '{}:{:02d}'.format(int(mins), int(secs))

        return '#{}: {} ({} vs. {}, {}, {})'.format(
            self.pk,
            self.scenario or 'Game',
            self.blueTeamName, self.redTeamName,
            self.getScoreString(),
            duration,
        )

    def getScoreString(self):
        if not self.winningTeam:
            scores = '½-½'
        elif self.winningTeam == 'A':
            scores = '1-0'
        else:
            scores = '0-1'
        return scores


class GamePlayer(models.Model):
    game = models.ForeignKey(GameRecord, on_delete=models.CASCADE)
    user = models.ForeignKey(TrosnothUser, null=True, blank=True, on_delete=models.SET_NULL)
    bot = models.BooleanField(default=False)
    botName = models.TextField(blank=True, default='')
    team = models.CharField(max_length=1, blank=True)

    coinsEarned = models.IntegerField(default=0)
    coinsWasted = models.IntegerField(default=0)
    coinsUsed = models.IntegerField(default=0)
    kills = models.IntegerField(default=0)
    deaths = models.IntegerField(default=0)
    zoneTags = models.IntegerField(default=0)
    zoneAssists = models.IntegerField(default=0)
    zoneScore = models.FloatField(default=0)
    shotsFired = models.IntegerField(default=0)
    shotsHit = models.IntegerField(default=0)
    timeAlive = models.FloatField(default=0)
    timeDead = models.FloatField(default=0)
    killStreak = models.IntegerField(default=0)
    tagStreak = models.IntegerField(default=0)
    aliveStreak = models.FloatField(default=0)
    boardScore = models.FloatField(default=0)

    class Meta:
        unique_together = ('game', 'user')

    def __str__(self):
        return '{}: {}'.format(self.nameStr(), self.game)

    def getNick(self):
        if self.user:
            return self.user.nick
        return self.botName

    def nameStr(self):
        if self.user:
            return '{}'.format(self.user)
        if self.bot:
            return '{} (bot)'.format(self.botName)
        return '{} (unregistered)'.format(self.botName)


class UpgradesUsedInGameRecord(models.Model):
    gamePlayer = models.ForeignKey(GamePlayer, on_delete=models.CASCADE)
    upgrade = models.CharField(max_length=1)
    count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('gamePlayer', 'upgrade')

    def __str__(self):
        return '{}: {}: {}'.format(self.gamePlayer, self.upgrade, self.count)


class PlayerKills(models.Model):
    killer = models.ForeignKey(
        GamePlayer, related_name='+', null=True, blank=True,
        on_delete=models.CASCADE)
    killee = models.ForeignKey(
        GamePlayer, related_name='+', on_delete=models.CASCADE)
    count = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Player kills records'
        unique_together = ('killer', 'killee')

    def __str__(self):
        return '{}: {} killed {}: {}'.format(
            self.getGame(),
            self.killer.nameStr() if self.killer else 'no-one',
            self.killee.nameStr(),
            self.count,
        )

    def getGame(self):
        return self.killee.game
