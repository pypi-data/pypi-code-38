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

from trosnoth.gui.app import MultiWindowApplication
from trosnoth.gui.framework import framework, elements, hotkey, prompt
from trosnoth.gui.framework.dialogbox import MoveableBox, DialogBox, YesNoBox, YesNoCancelBox, OkCancelBox, OkBox, DialogResult
from trosnoth.gui.common import Area, ScaledSize
from trosnoth.gui.fonts.font import ScaledFont
import pygame

class Interface(framework.CompoundElement):
    def __init__(self, app):
        super(Interface, self).__init__(app)

        # Draw the background
        bg = pygame.surface.Surface(app.screenManager.scaledSize)
        bg.fill((0,128,0))
        from random import randint
        for x in range(0,20):
            randPos = (randint(0,580), randint(0,430))
            pygame.draw.rect(bg, (255,0,0), pygame.rect.Rect(randPos, (20,20)), 10)
        box = FunBox(app, 'Disgusting Colour Scheme?')
        box._setPos((0,0))

        box2 = FunBox(app, 'Heck Yes!')
        box2.setColours(borderColour = (192,0,192))
        box3 = FunBox(app, '')
        box3._setPos((10,10))
        box4 = YesNoBox(app, (300,200), 'A question: ', 'Is Trosnoth cool?')
        box4.onClose.addListener(lambda:OkBox(app, (200,100), 'Result',
                'You pressed %s' % DialogResult.text[box4.result]).show())
        self.elements = [elements.PictureElement(app, bg)]
        box.onClose.addListener(lambda:self.app.screenManager.setScreenProperties((1024,768), 0, 'Testing'))
        box3.show()
        box.show()
        box2.show()
        box4.show()
        
        
##class FunBox(DialogBox):
class FunBox(MoveableBox):
    def __init__(self, app, textBoxText):
        
        super(FunBox, self).__init__(app, ScaledSize(300,200), 'Dialog!!')
        h = prompt.InputBox(app, Area((10,10), (280,50)), textBoxText, font = app.screenManager.fonts.bigMenuFont)
        h.onClick.addListener(self.setFocus)
        font = ScaledFont('KLEPTOCR.TTF', 30)
        b = elements.TextButton(app, (150, 100), 'Close', font, (255,0,0), (20,100,200))
        b.onClick.addListener(lambda sender: self.close())
        self.elements = [h, b]
        self.setColours(titleColour = (255,0,0), backgroundColour = (255,128,0))

size = (600,450)        
        
if __name__ == "__main__":        
    a = MultiWindowApplication(size, 0, 'Testing', Interface)
    a.run()
