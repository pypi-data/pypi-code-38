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

import pyjamas.pjscore as pjscore
from pyjamas.rcallbacks.rcallback import RCallback


class RCBZoom(RCallback):
    def cbZoom(self):
        self.pjs.gView.scale(1./pjscore.PyJAMAS.zoom_factors[self.pjs.zoom_index],
                             1./pjscore.PyJAMAS.zoom_factors[self.pjs.zoom_index])
        self.pjs.zoom_index = (self.pjs.zoom_index+1) % len(pjscore.PyJAMAS.zoom_factors)
        #print(str(self.pjs.zoom_index))
        self.pjs.gView.scale(pjscore.PyJAMAS.zoom_factors[self.pjs.zoom_index], pjscore.PyJAMAS.zoom_factors[self.pjs.zoom_index])
        self.pjs.MainWindow.resize(self.pjs.width * self.pjs.zoom_factors[self.pjs.zoom_index],
                                   self.pjs.height * self.pjs.zoom_factors[self.pjs.zoom_index] + 60)
        self.pjs.statusbar.showMessage(str(self.pjs.curslice + 1) + '/' + str(self.pjs.n_frames) + ' zoom: ' + str(pjscore.PyJAMAS.zoom_factors[self.pjs.zoom_index]) + 'x')

        return True


