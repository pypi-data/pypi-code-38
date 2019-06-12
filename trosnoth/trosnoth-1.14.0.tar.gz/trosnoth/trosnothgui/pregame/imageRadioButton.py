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

from trosnoth.gui.framework import framework
from trosnoth.gui.framework.elements import PictureElement, TextElement
from trosnoth.gui.common import Location, AttachedPoint
from trosnoth.utils.event import Event
import pygame


class RadioButtonGroup(framework.CompoundElement):
    def __init__(self, app):
        super(RadioButtonGroup, self).__init__(app)
        self.elements = []
        self.selectedIndex = -1
        self.onSelectionChanged = Event()
        self.by_value = {}

    def add(self, radioButton):
        self.elements.append(radioButton)
        self.by_value[radioButton.value] = radioButton
        radioButton._joinGroup(self)

    def getSelectedValue(self):
        if self.selectedIndex == -1:
            return None
        else:
            return self.elements[self.selectedIndex].value

    def selected(self, radioButton):
        if radioButton in self.by_value:
            radioButton = self.by_value[radioButton]
        assert radioButton in self.elements, ("Cannot select a radiobutton "
                "that isn't in this group")

        newIndex = self.elements.index(radioButton)
        if newIndex == self.selectedIndex:
            return

        if self.selectedIndex != -1:
            self.elements[self.selectedIndex].deselected()
        self.selectedIndex = newIndex
        radioButton.selected()
        self.onSelectionChanged.execute(self.selectedIndex)


class ImageRadioButton(framework.CompoundElement):

    class IRB_background(framework.Element):
        def __init__(self, app, imageRadioButton):
            super(ImageRadioButton.IRB_background, self).__init__(app)
            self.imageRadioButton = imageRadioButton
            self.mouseOver = False

        def draw(self, surface):
            if self.imageRadioButton._selected:
                colour = self.app.theme.colours.radioSelected
            elif self.mouseOver:
                colour = self.app.theme.colours.radioMouseover
            else:
                colour = self.app.theme.colours.radioUnselected
            surface.fill(colour, self.imageRadioButton._getRect())

        def processEvent(self, event):
            rect = self.imageRadioButton._getRect()
            # Passive events.
            if event.type == pygame.MOUSEMOTION:
                self.mouseOver = rect.collidepoint(event.pos)

            # Active events.
            if (event.type == pygame.MOUSEBUTTONDOWN and
                    rect.collidepoint(event.pos)):
                self.imageRadioButton._clicked()
                return None
            else:
                return event


    def __init__(self, app, text, area, image, value=None):
        super(ImageRadioButton, self).__init__(app)
        textLoc = Location(AttachedPoint((0,0), self._getRect, 'midbottom'),
                'midbottom')
        font = app.screenManager.fonts.smallNoteFont
        self.text = TextElement(app, text, font, textLoc, (0,0,0))
        picLoc = Location(AttachedPoint((0,0), self._getRect, 'midtop'),
                'midtop')
        self.area = area

        self.value = value

        self._selected = False
        self.group = None

        self.bg = self.IRB_background(app, self)

        self.elements = [self.bg, self.text]

        if image is not None:
            self.image = PictureElement(app, image, picLoc)
            self.elements.insert(1, self.image)


    def _beforeSelected(self):
        return True

    def _clicked(self):
        assert self.group, ("Image Radio Buttons are required to belong to "
                "a RadioButtonGroup")
        if self._beforeSelected():
            self.group.selected(self)

    def _getRect(self):
        return self.area.getRect(self.app)

    # Should only be called by the parent radio button group
    def _joinGroup(self, group):
        self.group = group

    def selected(self):
        self._selected = True

    def deselected(self):
        self._selected = False

    def draw(self, surface):
        super(ImageRadioButton, self).draw(surface)
        pygame.draw.rect(surface, self.app.theme.colours.black,
                         self._getRect(), 2)
