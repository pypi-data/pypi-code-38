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

from .framework import Element, CompoundElement
from .elements import TextButton, TextElement
from trosnoth.gui.common import (translateEvent, Location, addPositions,
    AttachedPoint, Relative)
from trosnoth.gui.errors import MultiWindowException
from trosnoth.gui.framework.utils import wrapWords
from trosnoth.utils.event import Event
from trosnoth.utils.utils import new
import pygame

class MoveableBox(CompoundElement):
    defaultBorderColour = (0,0,255)
    defaultTitleColour = (255,255,255)
    defaultBackgroundColour = (255,255,255)

    def __init__(self, app, size, caption, subCaption=None):
        CompoundElement.__init__(self, app)
        self.showing = False
        self.size = size
        self._edge = MoveableBoxEdge(self.app, self, caption, subCaption)

        self.setColours(self.defaultBorderColour, self.defaultTitleColour,
                self.defaultBackgroundColour)

        self.onClose = Event()

    def _giveFocus(self):
        self.app.screenManager.dialogFocus(self)

    def _getSize(self):
        if hasattr(self.size, 'getSize'):
            return self.size.getSize(self.app)
        else:
            return self.size

    def _setPos(self, pos):
        self._edge._setPos(pos)

    def setColours(self, borderColour=None, titleColour=None,
            backgroundColour=None):
        if borderColour:
            self._edge.borderColour = borderColour
        if titleColour:
            self._edge.titleColour = titleColour
        if backgroundColour:
            self.backgroundColour = backgroundColour

    def setCaption(self, caption=None, subCaption=None):
        if caption is not None:
            self._edge.caption = caption
        if subCaption is not None:
            if subCaption == False:
                self._edge.subCaption = None
            else:
                self._edge.subCaption = subCaption

    def _getPt(self):
        return self._edge._getInsideArea()

    def _getInsideRect(self):
        return pygame.Rect(self._edge._getInsideTopLeftPt(), self._getSize())

    def draw(self, screen):
        self._edge.draw(screen)
        subSurface = pygame.Surface(self._getSize())
        subSurface.fill(self.backgroundColour)
        CompoundElement.draw(self, subSurface)
        screen.blit(subSurface, self._edge._getInsideTopLeftPt())

    def processEvent(self, event):
        event = self._edge.processEvent(event)
        if event:
            if hasattr(event, 'pos'):
                event2 = translateEvent(event, self._edge._getInsideTopLeftPt())
                isPos = True
            else:
                event2 = event
                isPos = False
            event2 = CompoundElement.processEvent(self, event2)
            if event2 == None:
                return None
            elif isPos and self._edge._getEdgeRect().collidepoint(event.pos):
                return None
            else:
                return event

    def show(self):
        try:
            showDialog = self.app.screenManager.showDialog
        except AttributeError:
            raise MultiWindowException(
                'Dialog Boxes cannot be used unless the Application is a '
                'MultiWindowApplication')
        showDialog(self)
        self.showing = True

    def close(self):
        try:
            closeDialog = self.app.screenManager.closeDialog
        except AttributeError:
            raise MultiWindowException('Dialog Boxes cannot be used unless the '
                    'Application is a MultiWindowApplication')
        closeDialog(self)
        self.showing = False
        self.onClose.execute()

class DialogBox(MoveableBox):
    flashTime = 0.15
    flashNum = 2
    def __init__(self, app, size, caption, subCaption=None):
        MoveableBox.__init__(self, app, size, caption, subCaption)
        self.timeToFlash = 0

    def Relative(self, x, y):
        '''
        Returns an object representing a position relative to this dialogue box.
        See common.Relative() for more information.
        '''
        def getRect():
            return getInsideRectFromZero(self)
        return Relative(getRect, x, y)

    def processEvent(self, event):
        event = MoveableBox.processEvent(self, event)
        if event:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # It was clicked, but not within us.
                self.timeToFlash = self.flashNum * self.flashTime * 2
                # (Times 2 because we flash on and off)

            # We want to hold any messages except quit ones
            if event.type == pygame.QUIT:
                return event
        return None

    def tick(self, deltaT):
        if self.timeToFlash > 0:
            self.timeToFlash = max(self.timeToFlash - deltaT, 0)
        MoveableBox.tick(self, deltaT)

    def draw(self, screen):
        if self.timeToFlash > 0:
            phase = int(self.timeToFlash / self.flashTime) % 2
            if (phase == 1 and self.__normalBorderColour ==
                    self._edge.borderColour):
                invert = lambda x: tuple([255-i for i in x])
                MoveableBox.setColours(self,
                        borderColour=invert(self.__normalBorderColour),
                        titleColour=invert(self.__normalTitleColour))
            elif (phase == 0 and self.__normalBorderColour !=
                    self._edge.borderColour):
                MoveableBox.setColours(self,
                        borderColour=self.__normalBorderColour,
                        titleColour=self.__normalTitleColour)
        MoveableBox.draw(self, screen)

    def setColours(self, borderColour=None, titleColour=None,
            backgroundColour=None):
        MoveableBox.setColours(self, borderColour, titleColour,
                backgroundColour)
        self.__normalBorderColour = self._edge.borderColour
        self.__normalTitleColour = self._edge.titleColour
        self.timeToFlash = 0

    def setCaption(self, caption=None, subCaption=None):
        MoveableBox.setCaption(self, caption, subCaption)

class MessageBox(DialogBox):
    '''buttons = a tuple of DialogResults'''
    def __init__(self, app, size, caption, message, buttons):
        DialogBox.__init__(self, app, size, caption)
        if hasattr(size, 'getSize'):
            size = size.getSize(app)
        textFont = app.screenManager.fonts.labelFont
        lines = wrapWords(app, message, textFont, size[0])
        y = 5
        for text in lines:
            textPos = Location(DialogBoxAttachedPoint(self, (0, y), 'midtop'),
                    'midtop')
            self.elements.append(TextElement(app, text, textFont, textPos))
            y += textFont.getHeight(app)
        buttonFont = app.screenManager.fonts.captionFont
        for x in range(0, len(buttons)):
            dialogResult = buttons[x]
            location = Location(DialogBoxAttachedPoint(self, (0,
                    -textFont.getHeight(self.app) / 2), 'midbottom'),
                    'midbottom')
        buttonFont = app.screenManager.fonts.captionFont
        for x in range(0, len(buttons)):
            dialogResult = buttons[x]
            location = Location(((x + 1) * size[0] / (len(buttons) + 1), size[1]
                    * 2 / 3), 'midtop')
            button = TextButton(app, location, DialogResult.text[dialogResult],
                    buttonFont, (255,0,0), (255,100,200))
            button._mbResult = dialogResult
            button.onClick.addListener(self._setResultAndClose)
            self.elements.append(button)
        self.result = None

    def _setResultAndClose(self, button):
        self.result = button._mbResult
        self.close()

class YesNoBox(MessageBox):
    def __init__(self, app, size, caption, message):
        buttons = (DialogResult.Yes, DialogResult.No)
        MessageBox.__init__(self, app, size, caption, message, buttons)

class YesNoCancelBox(MessageBox):
    def __init__(self, app, size, caption, message):
        buttons = (DialogResult.Yes, DialogResult.No, DialogResult.Cancel)
        MessageBox.__init__(self, app, size, caption, message, buttons)

class OkBox(MessageBox):
    def __init__(self, app, size, caption, message):
        buttons = tuple([DialogResult.OK])
        MessageBox.__init__(self, app, size, caption, message, buttons)

class OkCancelBox(MessageBox):
    def __init__(self, app, size, caption, message):
        buttons = (DialogResult.OK, DialogResult.Cancel)
        MessageBox.__init__(self, app, size, caption, message, buttons)

class OkRetryBox(MessageBox):
    def __init__(self, app, size, caption, message):
        buttons = (DialogResult.OK, DialogResult.Retry)
        MessageBox.__init__(self, app, size, caption, message, buttons)

class DialogResult(object):
    OK, Cancel, Yes, No, Retry = new(5)
    text = {OK: 'OK', Cancel: 'Cancel', Yes: 'Yes', No: 'No', Retry: 'Retry'}


def getInsideRectFromZero(box):
    r = box._getInsideRect()
    r.topleft = (0,0)
    return r

def DialogBoxAttachedPoint(box, val, anchor='topleft'):
    return AttachedPoint(val, lambda:getInsideRectFromZero(box), anchor)

class MoveableBoxEdge(Element):
    '''
    Handles the border (including dragging and dropping) of boxes. It also
    handles the position of the box (so the box must query the edge to find its
    top left)
    '''
    def __init__(self, app, box, caption, subCaption=None):
        Element.__init__(self, app)
        self.box = box
        self.font = app.screenManager.fonts.captionFont
        self.smallFont = app.screenManager.fonts.keymapFont
        self.caption = caption
        self.subCaption = subCaption
        self.beingDragged = False
        self.borderWidth = 3
        appSize = app.screenManager.size
        self._setPos(tuple([(appSize[i] - self._getFullSize()[i]) / 2 for i
                in (0,1)]))

    def _getFullSize(self):
        return (self._getFullWidth(), self.box._getSize()[1] +
                self.borderWidth + self._getHeaderHeight())

    def _setPos(self, pos):
        self.pos = pos

    def __movedBy(self, difference):
        self._setPos(addPositions(difference, self.pos))

    def _getInsideTopLeftPt(self):
        return addPositions(self.pos, (self.borderWidth,
                self._getHeaderHeight()))

    def _getHeaderHeight(self):
        return int(self.font.getLineSize(self.app) * 1.5)

    def _getFullWidth(self):
        return self.box._getSize()[0] + self.borderWidth * 2

    def _getHeaderRect(self):
        r = pygame.rect.Rect(self.pos, (self._getFullWidth(),
                self._getHeaderHeight()))
        return r

    def _getEdgeRect(self):
        return pygame.Rect(self.pos, (self._getFullSize()))

    def isPointInRect(self, pos):
        return self._getEdgeRect().collidepoint(pos)

    def isPointInHeader(self, pos):
        return self._getHeaderRect().collidepoint(pos)

    def processEvent(self, event):
        if (event.type == pygame.MOUSEBUTTONDOWN and
                self.isPointInRect(event.pos)):
            self.box._giveFocus()
        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and
                self.isPointInHeader(event.pos)):
            self.beingDragged = True
            return None
        elif event.type == pygame.MOUSEMOTION and self.beingDragged:
            self.__movedBy(event.rel)
            return None
        elif (event.type == pygame.MOUSEBUTTONUP and event.button == 1 and
                self.beingDragged == True):
            self.beingDragged = False
            return None
        return event

    def draw(self, screen):
        screen.fill(self.borderColour, self._getEdgeRect())
        # Make pretty edges:
        setOuterBorder = lambda x, y: min(x + y, 255)
        outerBorder1 = tuple([setOuterBorder(self.borderColour[i], 70)
                for i in (0,1,2)])
        outerBorder2 = tuple([setOuterBorder(self.borderColour[i], 35)
                for i in (0,1,2)])
        pygame.draw.rect(screen, outerBorder1, self._getEdgeRect(), 1)
        if self.borderWidth > 2:
            oldRect = self._getEdgeRect()
            newRect = pygame.rect.Rect(oldRect.left + 1, oldRect.top + 1,
                    oldRect.width - 2, oldRect.height - 2)
            pygame.draw.rect(screen, outerBorder2, newRect, 1)

        text = self.font.render(self.app, self.caption, True,
                self.titleColour, self.borderColour)
        if self.subCaption is None:
            height = int(self.font.getLineSize(self.app) * 0.25)
        else:
            height = int(self.font.getLineSize(self.app) * 0.1)
        screen.blit(text, addPositions(self.pos, (self.borderWidth + 5,
                height)))
        if self.subCaption is not None:
            subText = self.smallFont.render(self.app, self.subCaption, True,
                    self.titleColour)
            height = int(self.font.getLineSize(self.app) * 0.8)
            screen.blit(subText, addPositions(self.pos, (self.borderWidth +
                    5, height)))

