# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2012 Joshua D Bartlett
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

from trosnoth.messages import SetTeamAbilitiesMsg
from trosnoth.model.settingsmanager import SettingsSynchroniser


class Team(object):
    '''Represents a team of the game'''
    def __init__(self, world, teamID, teamColour):
        self.world = world
        self.numZonesOwned = 0
        self.colour = teamColour

        self.usingMinimapDisruption = False
        self.abilities = SettingsSynchroniser(
            self._dispatchAbilitiesMsg,
            {
                'aggression': True,
                'zoneCaps': True,
            },
        )

        if (not isinstance(teamID, bytes)) or len(teamID) != 1:
            raise TypeError('teamID must be a single byte')
        self.id = teamID

        if teamID == b'A':
            self.teamName = 'Blue players'
        elif teamID == b'B':
            self.teamName = 'Red players'
        else:
            self.teamName = '%s Team' % (teamID,)

    def __str__(self):
        return self.teamName

    def _dispatchAbilitiesMsg(self, data):
        assert self.world.isServer
        self.world.sendServerCommand(SetTeamAbilitiesMsg(self.id, data))

    def zoneLost(self):
        '''Called when a orb belonging to this team has been lost'''
        self.numZonesOwned -= 1

    def zoneGained(self, score=0):
        '''Called when a orb has been attributed to this team'''
        self.numZonesOwned += 1

    @staticmethod
    def setOpposition(teamA, teamB):
        teamA.opposingTeam = teamB
        teamB.opposingTeam = teamA
