import logging

import pygame

from trosnoth.gui.framework import framework
from trosnoth.trosnothgui.common import setAlpha

log = logging.getLogger(__name__)


class GaugeBase(framework.Element):
    def __init__(self, app, area):
        super(GaugeBase, self).__init__(app)
        self.area = area

        self.icon = self.getIcon()
        if self.icon is not None:
            self.icon = self.icon.copy()
            setAlpha(self.icon, 160)

    def draw(self, surface):
        rect = self.area.getRect(self.app)
        pos = rect.topleft
        ratio = min(1, max(0, self.getRatio()))
        amount = int(ratio * rect.width)

        backColour = self.getBackColour()
        if backColour is not None:
            backRect = pygame.rect.Rect(
                pos[0] + amount, pos[1], rect.width - amount + 1, rect.height)
            surface.fill(backColour, backRect)

        if amount > 0:
            insideRect = pygame.rect.Rect(pos, (amount, rect.height))
            surface.fill(self.getForeColour(), insideRect)

        # Draw the border on top
        pygame.draw.rect(surface, self.app.theme.colours.gaugeBorder, rect, 2)

        if self.icon is not None:
            r = self.icon.get_rect()
            r.center = rect.midleft
            r.left -= r.width // 5
            surface.blit(self.icon, r)

    def getRatio(self):
        '''
        Return a number as a proportion (0..1) of how complete
        this box is. To be implemented in subclasses
        '''
        raise NotImplementedError

    def getForeColour(self):
        '''
        Return the foreground colour that this gauge should be.
        To be implemented in subclasses
        '''
        raise NotImplementedError

    def getBackColour(self):
        '''
        Return the background colour that this gauge should be.
        None = blank
        To be implemented in subclasses
        '''
        return None

    def getIcon(self):
        return None


class RespawnGauge(GaugeBase):
    '''Represents a graphical gauge to show how close to respawning a player
    is.'''
    def __init__(self, app, area, player, world):
        self.player = player
        self.world = world
        super(RespawnGauge, self).__init__(app, area)

    def getRatio(self):
        return 1 - (
            self.player.timeTillRespawn /
            self.player.world.physics.playerRespawnTotal)

    def getForeColour(self):
        if self.getRatio() >= 1:
            return self.app.theme.colours.gaugeGood
        else:
            return self.app.theme.colours.gaugeBad

    def getIcon(self):
        return self.app.theme.sprites.ghostIcon(self.player.team).getImage()


class GunGauge(GaugeBase):
    player = None

    def getRatio(self):
        player = self.player
        if player is None:
            return 0

        if player.machineGunner and player.machineGunner.bulletsRemaining > 0:
            return player.machineGunner.bulletsRemaining / 15.

        if player.reloadTime > 0:
            return 1 - player.reloadTime / (player.reloadFrom + 0.)

        return 1

    def getForeColour(self):
        player = self.player
        if player.machineGunner and player.machineGunner.bulletsRemaining > 0:
            return self.app.theme.colours.gaugeGood
        if player is None or player.reloadTime > 0:
            return self.app.theme.colours.gaugeBad
        return self.app.theme.colours.gaugeGood

    def getIcon(self):
        return self.app.theme.sprites.gunIcon.getImage()


class SingleUpgradeGauge(GaugeBase):
    '''Represents a graphical gauge to show how much time a player has left
    to use their upgrade.'''

    def __init__(self, app, area, item):
        self.item = item
        super(SingleUpgradeGauge, self).__init__(app, area)

    def getRatio(self):
        item = self.item
        if item.totalTimeLimit == 0:
            return 1
        return item.timeRemaining / item.totalTimeLimit

    def getForeColour(self):
        return self.app.theme.colours.gaugeGood

    def getIcon(self):
        return self.app.theme.sprites.upgradeImage(type(self.item))


class CoinGauge(GaugeBase):
    '''
    Shows how your teams coins are going compared to the number required for
    the selected upgrade.
    '''

    def __init__(self, app, area, player, upgrade):
        self.player = player
        self.upgrade = upgrade
        super(CoinGauge, self).__init__(app, area)

    def getRatio(self):
        if not self.upgrade.enabled:
            return 1
        if self.upgrade.requiredCoins == 0:
            return 1
        return self.player.coins / (self.upgrade.requiredCoins + 0.)

    def getForeColour(self):
        if not self.upgrade.enabled:
            return self.app.theme.colours.gaugeBad
        if self.getRatio() < 1:
            return self.app.theme.colours.gaugeBad
        return self.app.theme.colours.gaugeGood
