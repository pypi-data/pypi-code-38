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

import logging

from trosnoth.model.physics import CollisionCircle
from trosnoth.model.shot import LocalSprite
from trosnoth.model.unit import Bouncy, CollectableUnit, PredictedBouncyTrajectory

log = logging.getLogger(__name__)


class Trosball(Bouncy, CollectableUnit):
    # The following values control coin movement.
    maxFallVel = 540            # pix/s
    gravity = 1000              # pix/s/s
    ignoreLedges = False

    RADIUS = 10
    collisionShape = CollisionCircle(RADIUS)

    def __init__(self, world, *args, **kwargs):
        super(Trosball, self).__init__(world, *args, **kwargs)

        layout = world.map.layout
        self.pos = self.oldPos = (layout.centreX, layout.centreY)

        self.xVel = 0
        self.yVel = 0

        self.inNet = False

    def checkCollision(self, player, delay):
        if self.inNet:
            return False
        if self.world.trosballManager.getCooldownPlayer() == player:
            return False
        return super(Trosball, self).checkCollision(player, delay)

    def collidedWithPlayer(self, player):
        self.world.trosballManager.giveToPlayer(player)

    def setIsInNet(self, pos):
        self.pos = self.oldPos = pos
        self.xVel = 0
        self.yVel = 0
        self.inNet = True

    def advance(self):
        if not self.inNet:
            super(Trosball, self).advance()
            if not self.world.map.isInMap(self.pos):
                self.world.trosballManager.resetToStartLocation()

    def getGravity(self):
        return self.gravity

    def getMaxFallVel(self):
        return self.maxFallVel

    def teleport(self, pos, xxx_todo_changeme):
        (xVel, yVel) = xxx_todo_changeme
        self.pos = self.oldPos = pos
        self.xVel = xVel
        self.yVel = yVel
        self.hitLocalPlayer = False
        self.inNet = False

        
class PredictedTrosballTrajectory(PredictedBouncyTrajectory):
    collisionShape = Trosball.collisionShape

    def __init__(self, world, player):
        PredictedBouncyTrajectory.__init__(self, world, player, 4, world.physics.trosballThrowVel, Trosball.gravity, Trosball.maxFallVel)


class LocalTrosball(LocalSprite, Trosball):
    def collidedWithPlayer(self, player):
        pass
