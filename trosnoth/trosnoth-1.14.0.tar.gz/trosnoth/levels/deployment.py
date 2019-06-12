#!/usr/bin/env python3
if __name__ == '__main__':
    import os, sys
    sys.path.insert(0, os.path.join(
        os.path.abspath(os.path.dirname(__file__)), '..', '..'))

    # Install the asyncio reactor as early as possible
    import asyncio
    from twisted.internet import asyncioreactor
    asyncioreactor.install(asyncio.get_event_loop())

import random

from trosnoth.levels.base import playLevel
from trosnoth.levels.standard import StandardLevel
from trosnoth.model.map import ZoneStep, ZoneLayout


class DeploymentLevel(StandardLevel):
    def setupMap(self):
        super(DeploymentLevel, self).setupMap()

        blockRatio = 0.8

        zones = ZoneLayout(symmetryEnforced=True)

        def addColumn(startLocation, columnHeight, previousHeight):
            if not zones.hasZoneAt(startLocation):
                zones.addZoneAt(startLocation)

            current = startLocation
            connections = []
            for i in range(columnHeight - 1):
                nextLocation = current + ZoneStep.SOUTH
                zones.addZoneAt(nextLocation)
                connections.append((current, ZoneStep.SOUTH))
                current = nextLocation

            if previousHeight:
                if previousHeight < columnHeight:
                    assert previousHeight == columnHeight - 1
                    connections.append((startLocation, ZoneStep.SOUTHWEST))
                    connections.append((current, ZoneStep.NORTHWEST))
                    current = startLocation + ZoneStep.SOUTH
                    count = previousHeight - 1
                else:
                    assert previousHeight == columnHeight + 1
                    current = startLocation
                    count = columnHeight

                for i in range(count):
                    connections.append((current, ZoneStep.NORTHWEST))
                    connections.append((current, ZoneStep.SOUTHWEST))
                    current += ZoneStep.SOUTH

            while connections:
                loc, direction = connections.pop(0)
                if random.random() >= blockRatio:
                    zones.connectZone(loc, direction)

        location = zones.firstLocation
        addColumn(location, 5, 0)
        location += ZoneStep.SOUTHEAST
        addColumn(location, 4, 5)
        location += ZoneStep.NORTHEAST
        addColumn(location, 5, 4)
        location += ZoneStep.SOUTHEAST
        addColumn(location, 4, 5)
        location += ZoneStep.SOUTHEAST
        addColumn(location, 3, 4)
        location += ZoneStep.SOUTHEAST
        addColumn(location, 2, 3)
        location += ZoneStep.SOUTHEAST
        addColumn(location, 1, 2)

        zones.makeEverywhereReachable()
        layout = zones.createMapLayout(self.world.layoutDatabase)
        self.world.setLayout(layout)

        leftmost = min(self.world.zones, key=lambda z: z.defn.pos[0])
        rightmost = max(self.world.zones, key=lambda z: z.defn.pos[0])
        for zone in self.world.zones:
            if zone not in (leftmost, rightmost):
                if zone.owner:
                    zone.owner.zoneLost()
                zone.owner = None


if __name__ == '__main__':
    playLevel(DeploymentLevel(), aiCount=9)