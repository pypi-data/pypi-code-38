import logging
import os
import time

import simplejson
from trosnoth.data import getPath, user, makeDirs
from trosnoth.gamerecording import replays, stats, statgeneration
from trosnoth.messages import SetTeamNameMsg
from trosnoth.network.networkDefines import validServerVersions, serverVersion

log = logging.getLogger(__name__)

gameDir = 'recordedGames'
gameExt = '.tros'
replayDir = os.path.join(gameDir, 'replays')
replayExt = '.trosrepl'
statDir = os.path.join(gameDir, 'stats')
statExt = '.trosstat'
htmlDir = os.path.join(gameDir, 'htmlStats')


def getFilename(alias, directory, ext, multipleFiles = True):
    # Figure out the filename to use for the main file
    gamePath = getPath(user, directory)
    makeDirs(gamePath)
    copyCount = 0
    succeeded = False
    if multipleFiles:
        while not succeeded:
            filename = '%s (%s)%s' % (alias, str(copyCount), ext)
            filePath = os.path.join(gamePath, filename)
            succeeded = not os.path.exists(filePath)
            copyCount += 1
    else:
        filename = '%s%s' % (alias, ext)
        filePath = os.path.join(gamePath, filename)
    return filePath

# Separate from the server version, which is to do with the
# types and content of network messages.
recordedGameVersion = 2


class RecordedGameException(Exception):
    pass


class GameRecorder(object):

    def __init__(
            self, game, world, saveReplay=False, gamePrefix=None,
            replayPath=replayDir):
        super(GameRecorder, self).__init__()
        if gamePrefix is None:
            gamePrefix = 'unnamed'
        self.alias = gamePrefix + ' game'
        self.game = game
        self.serverVersion = serverVersion
        self.world = world
        self.saveReplay = saveReplay
        if replayPath is None:
            replayPath = replayDir
        self.replayPath = replayPath
        self.currentlySaving = False
        self.replayFilename = None

    def consumeMsg(self, msg):
        if self.currentlySaving:
            self.replayRecorder.consumeMsg(msg)
            if isinstance(msg, SetTeamNameMsg):
                self.gameFile.teamNameChanged(msg.teamId, msg.name)

    def matchStarted(self):
        self.matchEnded()
        if self.saveReplay and self.world.scenarioManager.level.recordGame:
            self.startSaving()

    def matchEnded(self):
        self.stopSaving()

    def saveEverything(self):
        self.statRecorder.save()

    def startSaving(self):
        assert not self.currentlySaving
        self.currentlySaving = True
        filename = getFilename(self.alias, gameDir, gameExt)
        statsFilename = getFilename(self.alias, statDir, statExt)
        self.replayFilename = getFilename(
            self.alias, self.replayPath, replayExt)

        self.gameFile = RecordedGameFile(
            filename, sVersion=serverVersion,
            alias=self.alias, replayFilename=self.replayFilename,
            statsFilename=statsFilename,
        )
        self.gameFile.save()
        self.statRecorder = stats.StatKeeper(
            self, self.world, statsFilename)
        self.replayRecorder = replays.ReplayRecorder(self.world,
                self.replayFilename)

    def start(self):
        self.world.onStartMatch.addListener(self.matchStarted)
        self.world.onEndMatch.addListener(self.matchEnded)

    def stop(self):
        self.world.onStartMatch.removeListener(self.matchStarted)
        self.world.onEndMatch.removeListener(self.matchEnded)
        self.stopSaving()

    def stopSaving(self):
        if not self.currentlySaving:
            return
        self.saveEverything()
        self.replayRecorder.stop()
        self.statRecorder.stop()
        self.gameFile.gameFinished()
        self.replayFilename = None
        self.currentlySaving = False


class RecordedGame(object):
    def __init__(self, filename):
        self.filename = filename
        self.gameFile = RecordedGameFile(self.filename)
        self.gameFile.load()
        if not self.gameFile.isValid():
            raise RecordedGameException('Invalid game version')

    def serverInformation(self):
        return self.gameFile.serverInformation

    def wasFinished(self):
        return self.gameFile.wasFinished()

    def generateHtmlFile(self):
        '''
        Generate an html stats file, and return the url
        '''
        if self.gameFile.hasHtml():
            return self.gameFile.htmlFile
        self.htmlFile = getFilename(self.gameFile.alias, htmlDir, '.html')
        statgeneration.generateHtml(self.htmlFile, self.gameFile.statsFilename)
        self.gameFile.htmlGenerated(self.htmlFile)
        return self.htmlFile

    def viewStats(self, app):
        from trosnoth.client3d.base import browser
        browser.openPage(app, self.generateHtmlFile())

    def __getattr__(self, attr):
        return getattr(self.gameFile, attr)


class RecordedGameFile(object):
    def __init__(self, filename, sVersion=None, alias=None, replayFilename=None,
            statsFilename=None):
        self.filename = filename
        self.serverInformation = {}
        self.serverInformation['recordedGameVersion'] = recordedGameVersion
        self.serverInformation['serverVersion'] = sVersion
        self.serverInformation['alias'] = alias
        self.serverInformation['replayFilename'] = replayFilename
        self.serverInformation['statsFilename'] = statsFilename
        self.serverInformation['dateTime'] = ','.join(map(str, time.localtime()))
        self.serverInformation['unixTimestamp'] = time.time()
        self.serverInformation['halfMapWidth'] = 0
        self.serverInformation['mapHeight'] = 0
        self.serverInformation['teamAname'] = 'Blue'
        self.serverInformation['teamBname'] = 'Red'

    def gameFinished(self):
        self.serverInformation['gameFinishedTimestamp'] = time.time()
        self.save()

    def teamNameChanged(self, teamId, teamName):
        self.serverInformation['team%sname' % (teamId,)] = teamName
        self.save()

    def htmlGenerated(self, filename):
        self.serverInformation['htmlFile'] = filename
        self.save()

    ##
    # Overwrites any existing file
    def save(self):
        # No value may be null
        for value in self.serverInformation.values():
            assert value is not None
        with open(self.filename, 'w') as f:
            serverInfoString = simplejson.dumps(self.serverInformation, indent=4)
            f.write(serverInfoString)

    def load(self):
        file = open(self.filename, 'rU')
        lines = file.readlines()

        fullText = '\n'.join(lines)
        try:
            self.serverInformation = simplejson.loads(fullText)
        except ValueError:
            raise RecordedGameException('invalid file')

    def isValid(self):
        return self.serverInformation['serverVersion'] in validServerVersions

    def wasFinished(self):
        return 'gameFinishedTimestamp' in self.serverInformation

    def hasHtml(self):
        return 'htmlFile' in self.serverInformation

    def hasReplay(self):
        if self.replayFilename is None:
            return False
        return os.path.isfile(self.replayFilename)

    def hasStats(self):
        if self.statsFilename is None:
            return False
        return os.path.isfile(self.statsFilename)

    def __getattr__(self, key):
        return self.serverInformation[key]
