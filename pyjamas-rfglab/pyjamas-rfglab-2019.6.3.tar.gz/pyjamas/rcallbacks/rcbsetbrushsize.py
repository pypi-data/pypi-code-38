"""
    PyJAMAS is Just A More Awesome Siesta
    Copyright (C) 2018  Rodrigo Fernandez-Gonzalez (rodrigo.fernandez.gonzalez@utoronto.ca)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from .rcallback import RCallback
from PyQt5 import QtWidgets


class RCBSetBrushSize(RCallback):
    def cbSetBrushSize(self, sz: int=None) -> bool:
        '''
        Sets the size of the brush used to paint polygons.
        :return: int (selected brush size or -1 if cancelled)
        '''

        brush_size: int = 0
        ok_flag: bool = None

        if sz != None and sz != False:
            brush_size = sz
            ok_flag = True
        else:
            # Read user input for brush size.
            brush_size, ok_flag = QtWidgets.QInputDialog.getInt(None, 'Set brush size: ', 'Enter new size: ',
                    self.pjs.brush_size, 1)

        
        if ok_flag and brush_size > 0:
            self.pjs.brush_size = brush_size
            self.pjs.repaint()

            return True

        else:
            return False
