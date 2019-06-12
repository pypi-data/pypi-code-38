import logging
import os

from trosnoth.data import getPath, user, makeDirs
from trosnoth.gamerecording.gamerecorder import (
    RecordedGame, RecordedGameException, gameDir, gameExt, recordedGameVersion,
)

log = logging.getLogger(__name__)


class Archivist(object):
    def __init__(self):
        self.games = None

    def getGames(self):
        if self.games is None:
            self.refresh()
        return list(self.games)

    def refresh(self):
        # Get a list of files with the name '*.tros'
        logDir = getPath(user, gameDir)
        makeDirs(logDir)
        self.games = []

        for fname in os.listdir(logDir):
            if os.path.splitext(fname)[1] != gameExt:
                continue

            try:
                game = RecordedGame(os.path.join(logDir, fname))
            except RecordedGameException:
                continue

            if game.recordedGameVersion != recordedGameVersion:
                continue

            self.games.append(game)

        self.games.sort(key=lambda game: (-game.unixTimestamp, game.filename))
