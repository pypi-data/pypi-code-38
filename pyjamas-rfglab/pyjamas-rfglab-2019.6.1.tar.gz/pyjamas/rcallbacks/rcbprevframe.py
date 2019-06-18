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


class RCBPrevFrame(RCallback):
    def cbPrevFrame(self):
        if self.pjs.curslice > 0:
            self.pjs.curslice = self.pjs.curslice - 1
        elif self.pjs.curslice == 0:
            self.pjs.curslice = self.pjs.n_frames - 1

        self.pjs.imagedata = self.pjs.slices[self.pjs.curslice]
        self.pjs.timeSlider.setValue(self.pjs.curslice + 1)

        self.pjs.displayData()

        return True
