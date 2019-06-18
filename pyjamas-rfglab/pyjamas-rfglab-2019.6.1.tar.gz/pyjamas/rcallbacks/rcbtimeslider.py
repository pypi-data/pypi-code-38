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

from pyjamas.rcallbacks.rcallback import RCallback


# todo: merge the two methods into a single one that can accept one parameter.
class RCBTimeSlider(RCallback):
    def cbTimeSlider(self) -> bool:
        self.pjs.curslice = self.pjs.timeSlider.value()-1
        self.pjs.imagedata = self.pjs.slices[self.pjs.curslice]

        self.pjs.displayData()

        return True

    def cbGoTo(self, slice_index: int) -> bool:
        """

        :param slice_index: negative values start start pointing from the last slice (-1 being the last one).
        :return:
        """
        if slice_index >= self.pjs.n_frames:
            return False

        if slice_index < 0:
            slice_index = self.pjs.n_frames+slice_index
            if slice_index < 0:
                return False

        self.pjs.curslice = slice_index
        self.pjs.imagedata = self.pjs.slices[self.pjs.curslice]
        self.pjs.timeSlider.setValue(slice_index+1)

        self.pjs.displayData()

        return True

