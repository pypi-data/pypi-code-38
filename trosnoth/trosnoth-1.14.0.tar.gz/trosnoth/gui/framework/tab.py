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

from trosnoth.gui.framework.framework import CompoundElement
from trosnoth.gui.common import Relative

class Tab(CompoundElement):
    borderWidth = 4
    def __init__(self, app, caption):
        super(Tab, self).__init__(app)
        self.caption = caption
        self.container = None

    def Relative(self, x, y):
        '''
        Returns an object representing a position relative to this tab's canvas.
        See common.Relative() for more information.
        '''
        def getRect():
            return self.container._getTabInternalRect()
        return Relative(getRect, x, y)

    def activated(self):
        pass

    def beforeDeactivating(self):
        return True

    def deactivated(self):
        pass

    def __str__(self):
        return self.caption

    def __repr__(self):
        return self.caption
