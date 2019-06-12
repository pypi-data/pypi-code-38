import pygame

from trosnoth.gui.framework.elements import TextElement, PictureElement
from trosnoth.gui.common import (Area, FullScreenAttachedPoint, Location,
        ScaledSize)
import trosnoth.gui.framework.framework as framework
from trosnoth.gamerecording.achievementlist import availableAchievements
from trosnoth.utils.twist import WeakLoopingCall

class AchievementBox(framework.CompoundElement):
    achievementDefs = availableAchievements
    def __init__(self, app, player, achievementId):
        super(AchievementBox, self).__init__(app)
        self.app = app
        self.player = player

        self.achievements = [achievementId]

        self.width = 453
        self.height = 75

        self._setColours()

        self.area = Area(FullScreenAttachedPoint(
            ScaledSize(0, -100), 'midbottom'),
            ScaledSize(self.width, self.height), 'midbottom')

        self.smlBox = Area(FullScreenAttachedPoint(
                ScaledSize(-self.width / 2 + 6, -104), 'midbottom'),
                ScaledSize(66, 66), 'bottomleft')

        self.titleText = TextElement(self.app, 'ACHIEVEMENT UNLOCKED!',
                self.fonts.achievementTitleFont,
                Location(FullScreenAttachedPoint(ScaledSize(73 / 2, -100 -
                self.height + 10), 'midbottom'), 'midtop'), self.borderColour)

        self.nameText = TextElement(self.app,
                self.achievementDefs.getAchievementDetails(achievementId)[0],
                self.fonts.achievementNameFont,
                Location(FullScreenAttachedPoint(ScaledSize(73 / 2, -100 - 13),
                'midbottom'), 'midbottom'), self.colours.black)

        self.elements = [self.titleText, self.nameText]
        self._updateImage()

        self.cycler = WeakLoopingCall(self, 'cycleAchievements')
        self.cycler.start(5.0, now = False)

    def addAchievement(self, achievementId):
        self.achievements.append(achievementId)
        self.titleText.setText("%d ACHIEVEMENTS UNLOCKED!" %
                len(self.achievements))

    def _updateImage(self):
        try:
            filepath = self.app.theme.getPath('achievements', '%s.png' %
                    self.achievements[0])
        except IOError:
            filepath = self.app.theme.getPath('achievements', 'default.png')

        image = pygame.image.load(filepath)
        image = pygame.transform.smoothscale(image,
                ScaledSize(64, 64).getSize(self.app)).convert()

        if type(self.elements[-1]) == PictureElement:
            self.elements.pop()

        self.image = PictureElement(self.app, image,
                Location(FullScreenAttachedPoint(
                ScaledSize(-self.width / 2 + 7, -105), 'midbottom'),
                'bottomleft'))

        self.elements.append(self.image)

    def cycleAchievements(self):
        del self.achievements[0]

        if len(self.achievements) == 0:
            self.cycler.stop()
            return
        elif len(self.achievements) == 1:
            self.titleText.setText("ACHIEVEMENT UNLOCKED!")
        else:
            self.titleText.setText("%d ACHIEVEMENTS UNLOCKED!" %
                    len(self.achievements))

        self.nameText.setText(self.achievementDefs.getAchievementDetails(
                self.achievements[0])[0])
        self._updateImage()

    def _setColours(self):
        self.colours = self.app.theme.colours
        self.fonts = self.app.screenManager.fonts

        if self.player.teamId == b'A':
            self.borderColour = self.colours.achvBlueBorder
            self.bgColour = self.colours.achvBlueBackground
        else:
            self.borderColour = self.colours.achvRedBorder
            self.bgColour = self.colours.achvRedBackground

    def _getRect(self, area):
        return area.getRect(self.app)

    def draw(self, surface):
        mainRect = self._getRect(self.area)
        boxRect = self._getRect(self.smlBox)

        surface.fill(self.bgColour, mainRect)
        pygame.draw.rect(surface, self.borderColour, mainRect, 2)

        surface.fill(self.colours.white, boxRect)
        pygame.draw.rect(surface, self.borderColour, boxRect, 1)

        super(AchievementBox, self).draw(surface)

