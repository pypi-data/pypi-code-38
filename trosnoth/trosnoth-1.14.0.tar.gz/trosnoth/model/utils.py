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

import pygame

from trosnoth.model.map import MapLayout


class Rect(pygame.Rect):
    '''
    Represents rectangular regions of the map.
    '''
    pass


def getBlocksInRect(world, rect):
    '''
    Returns an iterator of the blocks in the given rect.
    '''
    i, j0 = MapLayout.getMapBlockIndices(rect.left, rect.top)
    j0 = max(0, j0)
    i = max(0, i)

    while i < len(world.zoneBlocks):
        row = world.zoneBlocks[i]
        j = j0
        while j < len(row):
            block = row[j]
            blockLeft, blockTop = block.defn.pos
            if blockTop >= rect.bottom:
                return
            if blockLeft >= rect.right:
                break
            yield block
            j += 1
        i += 1


def getZonesInRect(world, rect):
    '''
    This will yield all zones which are in map blocks in the given rect.
    Note that sometimes a zone will be yielded that is not quite in the rect,
    if one of the zone's map blocks is in the rect.
    '''
    touchedZones = set()
    for block in getBlocksInRect(world, rect):
        for zone in block.getZones():
            if zone not in touchedZones:
                touchedZones.add(zone)
                yield zone
