import logging
import pygame

from trosnoth.gui.common import (
    Location, FullScreenAttachedPoint, defaultAnchor, SizedImage,
    ScaledScreenSize, TextImage, RelativeLocation)
from trosnoth.utils.event import Event
from trosnoth.gui import colours

from .framework import Element

log = logging.getLogger(__name__)


class SolidRect(Element):
    '''
    Solid rectangle.
    '''
    def __init__(self, app, colour, alpha, region, border=None):
        super(SolidRect, self).__init__(app)
        self.image = None
        self.colour = colour
        self.border = border
        self.alpha = alpha
        self.region = region

        app.screenManager.onResize.addListener(self.refresh)

    def refresh(self):
        self.image = None

    def draw(self, screen):
        r = self.region.getRect(self.app)
        if self.image is None or self.image.get_rect() != r:
            self.image = pygame.Surface(r.size)
            self.image.fill(self.colour)
            if self.alpha is not None:
                self.image.set_alpha(self.alpha)

        screen.blit(self.image, r.topleft)
        if self.border:
            pygame.draw.rect(screen, self.border, r, 1)


class PictureElement(Element):
    '''Displays a picture at a specified screen location.

    @param pos: an instance of trosnoth.ui.common.Location
    '''
    def __init__(self, app, image, pos=None):
        super(PictureElement, self).__init__(app)
        self.setImage(image)
        if pos is None:
            pos = Location(FullScreenAttachedPoint((0, 0), 'center'), 'center')
        self.pos = pos

    def setImage(self, image):
        self.image = image

    def setPos(self, pos):
        self.pos = pos

    def draw(self, screen):
        if hasattr(self.image, 'getImage'):
            surface = self.image.getImage(self.app)
        else:
            surface = self.image

        rect = pygame.Rect(surface.get_rect())
        if hasattr(self.pos, 'apply'):
            self.pos.apply(self.app, rect)
        else:
            pos = self.pos
            setattr(rect, defaultAnchor, pos)

        screen.blit(surface, rect.topleft)


class SizedPicture(PictureElement):
    '''
    Display a picture scaled to the specified position.
    @param  pos         should be an instance of trosnoth.ui.common.Location
    '''
    def __init__(self, app, surface, pos, size):
        image = SizedImage(surface, size, colourkey=False)
        super(SizedPicture, self).__init__(app, image, pos)


# Convenience wrapper
class Backdrop(PictureElement):
    '''Display a picture scaled to the biggest 4:3 image that will fit in
    the window, with black filling the rest of the window.'''
    def __init__(self, app, name, colour):
        image = SizedImage(name, ScaledScreenSize(), False)
        self.colour = colour
        super(Backdrop, self).__init__(app, image)

    def draw(self, screen):
        if hasattr(self.image, 'getImage'):
            surface = self.image.getImage(self.app)
        else:
            surface = self.image

        rect = pygame.Rect(surface.get_rect())
        if hasattr(self.pos, 'apply'):
            self.pos.apply(self.app, rect)
        else:
            pos = self.pos
            setattr(rect, defaultAnchor, pos)

        sRect = screen.get_rect()
        if 0 < rect.left:
            screen.fill(self.colour, rect=pygame.Rect(
                0, 0, rect.left, rect.bottom))
        if 0 < rect.top:
            screen.fill(self.colour, rect=pygame.Rect(
                rect.left, 0, sRect.width - rect.left, rect.top))
        if rect.right < sRect.right:
            screen.fill(self.colour, rect=pygame.Rect(
                rect.right, rect.top, sRect.width - rect.right,
                sRect.height - rect.top))
        if rect.bottom < sRect.bottom:
            screen.fill(self.colour, rect=pygame.Rect(
                0, rect.bottom, rect.right, sRect.height - rect.bottom))

        screen.blit(surface, rect.topleft)


class TextElement(Element):
    '''Shows text at a specified screen location.
    @param pos: should be an instance of trosnoth.ui.common.Location'''

    def __init__(
            self, app, text, font, pos, colour=(0, 128, 0),
            anchor='topleft', shadow=False, backColour=None,
            antialias=True):
        super(TextElement, self).__init__(app)

        self.pos = pos
        self.anchor = anchor
        self.image = TextImage(text, font, colour, backColour, antialias)
        self.__shadow = None
        self.setShadow(shadow)
        self._surface = None
        self.rect = None

        app.screenManager.onResize.addListener(self.appResized)

    def appResized(self):
        self.rect = None
        self._surface = None

    def _getImage(self):
        if self._surface is None:
            self.image.refresh()
            self._surface = self.image.getImage(self.app)
        return self._surface

    def getRect(self, app):
        assert app is self.app
        return self._getRect()

    def _getRect(self):
        if self.rect is not None:
            return self.rect

        rect = self._getImage().get_rect()
        pos = self.pos
        if hasattr(pos, 'apply'):
            pos.apply(self.app, rect)
        else:
            setattr(rect, defaultAnchor, pos)

        self.rect = rect
        return rect

    def getText(self):
        return self.image.text

    def setColour(self, colour):
        self.image.colour = colour
        self._surface = None

    def setText(self, text):
        if self.image.text != text:
            self._surface = None
            self.image.text = text
            if self.__shadow is not None:
                self.__shadow.setText(text)

    def setFont(self, font):
        if self.image.font != font:
            self.image.font = font
            if self.__shadow is not None:
                self.__shadow.setFont(font)
            self._surface = None

    def setPos(self, pos):
        if self.pos != pos:
            self.pos = pos
            if self.__shadow is not None:
                self.__shadow.setPos(self.__getShadowPos())
            self._surface = None
            self.rect = None

    def __getShadowPos(self):
        x = self._shadowOffset
        pos = RelativeLocation(self.pos, (x, x))
        return pos

    def setShadow(self, shadow, offset=None):
        if shadow:
            if self.__shadow is None:
                if offset is None:
                    height = self.image.font.getHeight(self.app)
                    self._shadowOffset = (height / 45) + 1
                else:
                    self._shadowOffset = offset

                self.__shadow = TextElement(
                    self.app, self.image.text,
                    self.image.font, self.__getShadowPos(),
                    colours.shadowDefault, self.anchor, False)
                self._surface = None
        else:
            if self.__shadow is not None:
                self.__shadow = None
                self._surface = None

    def setShadowOffset(self, offset):
        if self.__shadow is not None:
            self.setShadow(False)
            self.setShadow(True, offset)

    def setShadowColour(self, colour):
        if self.__shadow is not None:
            self.__shadow.setColour(colour)
            self._surface = None

    def draw(self, screen):
        if self.__shadow is not None:
            assert self.__shadow.__shadow is None
            self.__shadow.draw(screen)

        rect = self._getRect()

        # Adjust text position based on anchor.
        image = self._getImage()

        rectPos = getattr(rect, self.anchor)
        imagePos = getattr(image.get_rect(), self.anchor)
        pos = (rectPos[0]-imagePos[0], rectPos[1]-imagePos[1])

        screen.blit(image, pos)


class HoverButton(Element):
    '''A button which changes image when the mouse hovers over it.
    @param  pos     should be a trosnoth.ui.common.Location instance
    '''
    def __init__(
            self, app, pos, stdImage, hvrImage, hotkey=None, onClick=None):
        super(HoverButton, self).__init__(app)

        self.stdImage = stdImage
        self.hvrImage = hvrImage
        self.pos = pos
        self.onClick = Event()
        self.hotkey = hotkey

        self.mouseOver = False

        if onClick is not None:
            self.onClick.addListener(onClick)

    def _getSurfaceToBlit(self):
        img = self._getImageToUse()
        if hasattr(img, 'getImage'):
            return img.getImage(self.app)
        else:
            return img

    def _getImageToUse(self):
        if self.mouseOver:
            return self.hvrImage
        else:
            return self.stdImage

    def _getSize(self):
        img = self._getImageToUse()
        if hasattr(img, 'getSize'):
            return img.getSize(self.app)
        else:
            # pygame.surface.Surface
            return img.get_size()

    def _getPt(self):
        if hasattr(self.pos, 'apply'):
            rect = pygame.Rect((0, 0), self._getSize())
            self.pos.apply(self.app, rect)
            return rect.topleft
        else:
            return self.pos

    def _getRect(self):
        if hasattr(self.pos, 'apply'):
            rect = pygame.Rect((0, 0), self._getSize())
            self.pos.apply(self.app, rect)
            return rect
        return pygame.Rect(self.pos, self._getSize())

    def processEvent(self, event):
        rect = self._getRect()
        # Passive events.
        if event.type == pygame.MOUSEMOTION:
            self.mouseOver = rect.collidepoint(event.pos)

        # Active events.
        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and
                rect.collidepoint(event.pos)):
            self.onClick.execute(self)
        elif event.type == pygame.KEYDOWN and event.key == self.hotkey:
            self.onClick.execute(self)
        else:
            return event
        return None

    def draw(self, screen):
        # Draw the button.
        screen.blit(self._getSurfaceToBlit(), self._getPt())


class TextButton(HoverButton):
    'A HoverButton which has text rather than images.'
    def __init__(
            self, app, pos, text, font, stdColour, hvrColour,
            hotkey=None, backColour=None, onClick=None):
        self.stdImage = TextImage(text, font, stdColour, backColour)
        self.hvrImage = TextImage(text, font, hvrColour, backColour)

        super(TextButton, self).__init__(
            app, pos, self.stdImage, self.hvrImage, hotkey, onClick)

        self.app.screenManager.onResize.addListener(self.appResized)

    def appResized(self):
        # The font may be scaled, so refresh the images
        self.stdImage.refresh()
        self.hvrImage.refresh()

    def setText(self, text):
        self.stdImage.text = text
        self.hvrImage.text = text

    def setFont(self, font):
        self.stdImage.setFont(font)
        self.hvrImage.setFont(font)

    def setColour(self, colour):
        self.stdImage.setColour(colour)

    def setHoverColour(self, colour):
        self.hvrImage.setColour(colour)

    def setBackColour(self, colour):
        self.hvrImage.setBackColour(colour)
        self.stdImage.setBackColour(colour)
