'''
leaderboard.py - defines the LeaderBoard class which deals with drawing the
leader board to the screen.
'''

import pygame
import logging

import trosnoth.gui.framework.framework as framework
from trosnoth.gui.common import Location, Scalar, FullScreenAttachedPoint
from trosnoth.gui.framework import table
from trosnoth.gui.framework.elements import SolidRect
from trosnoth.model.universe_base import NEUTRAL_TEAM_ID
from trosnoth.utils.twist import WeakCallLater

log = logging.getLogger(__name__)

# How often the leaderboard will update (in seconds)
UPDATE_DELAY = 1.0


class LeaderBoard(framework.CompoundElement):

    def __init__(self, app, game, gameViewer, shadow=False):
        super(LeaderBoard, self).__init__(app)
        self.world = game.world
        self.shadow = shadow
        self.gameViewer = gameViewer
        self.app = app
        self.scale = self.app.screenManager.scaleFactor

        self.xPos = 4
        self.yPos = (self.gameViewer.miniMap.getRect().bottom +
                self.gameViewer.zoneBarHeight + 5)
        position = Location(FullScreenAttachedPoint((self.xPos, self.yPos),
                'topright'), 'topright')

        # Create the table and set all the appropriate style attributes
        self.playerTable = table.Table(app, position, columns=4, topPadding=4)

        self.playerTable.setBorderWidth(0)
        self.playerTable.setBorderColour((0, 0, 0))

        self.playerTable.style.backColour = None
        self.playerTable.style.foreColour = app.theme.colours.leaderboardNormal
        self.playerTable.style.font = app.screenManager.fonts.leaderboardFont
        self.playerTable.style.padding = (4, 1)
        self.playerTable.style.hasShadow = shadow
        self.playerTable.style.shadowColour = (0, 0, 0)

        self.playerTable.getColumn(0).style.textAlign = 'midright'
        self.playerTable.getColumn(1).style.textAlign = 'midright'
        self.playerTable.getColumn(2).style.textAlign = 'midright'

        self.rowHeight = Scalar(25)

        self.playerTable.getColumn(0).setWidth(30)    # Flags
        self.playerTable.getColumn(1).setWidth(100)   # Name
        self.playerTable.getColumn(2).setWidth(70)    # Score
        self.playerTable.getColumn(3).setWidth(30)    # Padding

        self._resetPlayers()

        self.elements = [self.playerTable]

        bgColour = app.theme.colours.leaderboardBackground
        if bgColour[3]:
            background = SolidRect(
                app, bgColour, bgColour[3], self.playerTable)
            self.elements.insert(0, background)
        self.update(True)

    def _resetPlayers(self):
        self.players = dict((k, []) for k in self.world.teamWithId)

    def update(self, loop=False):
        self._resetPlayers()

        self.yPos = (self.gameViewer.miniMap.getRect().bottom +
                     self.gameViewer.zoneBarHeight + 5)
        if not self.world.uiOptions.showReadyStates:
            yPos = self.yPos
        else:
            yPos = self.yPos + int(50 * self.scale)
        self.playerTable.pos = Location(FullScreenAttachedPoint(
                (self.xPos, yPos), 'topright'), 'topright')

        try:
            pi = self.gameViewer.interface.runningPlayerInterface
            self.friendlyTeam = pi.player.team
            self.spectator = False
        except (AttributeError, KeyError):
            # This will occur if the player is not yet on a team
            self.friendlyTeam = self.world.teamWithId[b'A']
            self.spectator = True

        for player in self.world.players:
            # getDetailsForLeaderBoard() returns dict with pID, nick, team, dead, coins etc.
            details = player.getDetailsForLeaderBoard()
            self.players[details['team']].append(details)

        self._sortTeam(b'A')
        self._sortTeam(b'B')
        self._sortTeam(NEUTRAL_TEAM_ID)
        self._updateTable()

        if loop:
            self.callDef = WeakCallLater(UPDATE_DELAY, self, 'update', True)

    def _sortTeam(self, teamId):
        self.players[teamId].sort(key=lambda p: (
            None if p['score'] is None else -p['score'],
            p['pID'],
        ))

    def _updateTable(self):
        for x in range(self.playerTable.rowCount()):
            self.playerTable.delRow(0)

        index = -1
        self.contents = []

        if self.world.scoreboard and self.world.scoreboard.teamScoresEnabled:
            teamOrder = sorted(self.world.teams, key=lambda team: (
                -self.world.scoreboard.teamScores[team],
                not (team == self.friendlyTeam),
                team.id,
            )) + [None]
        else:
            teamOrder = []
            if self.friendlyTeam is not None:
                teamOrder.append(self.friendlyTeam)
            teamOrder.extend(
                t for t in self.world.teams if t != self.friendlyTeam)
            teamOrder.append(None)

        for team in teamOrder:
            if team is None:
                teamId = NEUTRAL_TEAM_ID
            else:
                teamId = team.id

            visiblePlayers = self.players[teamId]
            if len(visiblePlayers) == 0:
                continue

            index = self._addTeamHeader(team, teamId, visiblePlayers, index)

            # Add a row for each player
            for player in visiblePlayers:
                index = self._addPlayerRow(team, teamId, player, index)

    def _addRow(self, index, height):
        index += 1
        self.playerTable.addRow()
        row = self.playerTable.getRow(index)
        row.setHeight(height)
        return index

    def _writeTeamHeaderPlayerCount(self, players, index):
        if len(players) == 1:
            noun = 'player'
        else:
            noun = 'players'
        self.playerTable[2][index].setText(str(len(players)) + ' ' + noun)

    def _addTeamHeader(self, team, teamId, players, index):
        index = self._addRow(index, self.rowHeight)
        self.playerTable[0][index].setText(str(len(players)))
        self.playerTable[1][index].setText(self.world.getTeamName(teamId))

        scoreboard = self.world.scoreboard
        if scoreboard and team and scoreboard.teamScoresEnabled:
            teamScore = scoreboard.teamScores[team]
            if isinstance(teamScore, float):
                scoreText = '{:.1f}'.format(teamScore)
            else:
                scoreText = str(teamScore)
        else:
            scoreText = ''
        self.playerTable[2][index].setText(scoreText)

        teamColour = self.app.theme.colours.leaderboard(team)

        self.playerTable.getRow(index).style.foreColour = teamColour
        self.playerTable[0][index].style.foreColour = \
            self.app.theme.colours.leaderboardDead
        self.contents.append((index, 'header', team))

        return index

    def _setPlayerColour(self, team, player, index):
        if player['dead']:
            colour = self.app.theme.colours.leaderboardDead
        else:
            colour = self.app.theme.colours.leaderboard(team)
        self.playerTable[1][index].style.foreColour = colour
        self.playerTable[2][index].style.foreColour = colour

    def _addPlayerRow(self, team, teamId, player, index):
        index = self._addRow(index, self.rowHeight)

        flags = ''
        if self.world.uiOptions.showReadyStates:
            if player['ready']:
                flags = 'R'

        if player['score'] is None:
            scoreText = ''
        elif isinstance(player['score'], float):
            scoreText = '{:.1f}'.format(player['score'])
        else:
            scoreText = str(player['score'])

        self.playerTable[0][index].setText(flags)
        self.playerTable[1][index].setText(player['nick'])
        self.playerTable[2][index].setText(scoreText)

        self._setPlayerColour(team, player, index)

        return index

    def kill(self):
        self.callDef.cancel()

    def draw(self, surface):
        super(LeaderBoard, self).draw(surface)

        # pointA = left-most point of the line
        # pointB = right-most point of the line
        # pointC = left-most point of the line shadow
        # pointD = right-most point of the line shadow

        for (index, rowKind, team) in self.contents:
            if rowKind == 'header':
                rightMargin = int(8 * self.scale)
                leftMargin = int(10 * self.scale)
                bottomMargin = int(2 * self.scale)

                point = self.playerTable._getRowPt(index + 1)
                pointA = (point[0] + leftMargin, point[1] - bottomMargin)
                pointB = (pointA[0] + self.playerTable._getSize()[0] -
                        leftMargin - rightMargin, pointA[1])
                teamColour = self.app.theme.colours.leaderboard(team)
                pygame.draw.line(surface, teamColour, pointA, pointB, 1)
                if self.shadow:
                    pointC, pointD = shift(pointA, pointB)
                    pygame.draw.line(surface, (0, 0, 0), pointC, pointD, 1)

                pointA, pointB = shift(pointA, pointB,
                        -self.playerTable.getRow(index)._getHeight() +
                        bottomMargin, 0)
                teamColour = self.app.theme.colours.leaderboard(team)
                pygame.draw.line(surface, teamColour, pointA, pointB, 1)
                if self.shadow:
                    pointC, pointD = shift(pointA, pointB)
                    pygame.draw.line(surface, (0, 0, 0), pointC, pointD, 1)

            elif rowKind == 'total':
                bottomMargin = int(2 * self.scale)

                rowPoint = self.playerTable._getRowPt(index)
                colPoint = self.playerTable._getColPt(2)
                pointA = (colPoint[0], rowPoint[1] - bottomMargin)
                pointB = (pointA[0] + self.playerTable.getColumn(2)._getWidth(),
                        pointA[1])
                pygame.draw.line(surface,
                        self.app.theme.colours.leaderboardNormal, pointA,
                        pointB, 1)
                if self.shadow:
                    pointC, pointD = shift(pointA, pointB)
                    pygame.draw.line(surface, (0, 0, 0), pointC, pointD, 1)

def shift(pointA, pointB, down = 1, right = 1):
    '''Returns two points that are shifted by the specified number of pixels.
    Negative values shift up and left, positive values shift down and right.'''
    return ((pointA[0] + right, pointA[1] + down),
            (pointB[0] + right, pointB[1] + down))

