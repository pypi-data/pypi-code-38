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


class RCBFramesPerSec(RCallback):
    def cbFramesPerSec(self, fps: int=None) -> int:
        '''
        Sets the size of the brush used to paint polygons.
        :return: int (selected brush size or -1 if cancelled)
        '''

        thefps: int = 0
        ok_flag: bool = None

        if fps is not None and fps is not False:
            thefps = fps
            ok_flag = True
        else:
            # Read user input for fps.
            thefps, ok_flag = QtWidgets.QInputDialog.getInt(None, 'Set frames per second: ', 'Enter frames per second: ',
                                                            self.pjs.fps, 1)

        
        if ok_flag and thefps > 0:
            self.pjs.fps = thefps

            return True

        else:
            return False
