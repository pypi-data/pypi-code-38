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

from PyQt5 import QtCore, QtWidgets

import pyjamas.pjscore as pjscore
from pyjamas.rcallbacks.rcallback import RCallback
from pyjamas.rutils import RUtils


class RCBCopyPastePolyline(RCallback):

    PIX_SHIFT: int = 2  # x, y shift to use when pasting polylines with a shift with respect to original position.

    def cbCopyPolyline(self) -> bool:
        self.pjs.annotation_mode = pjscore.PyJAMAS.copy_polyline
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)

        return True

    def cbPastePolyline(self, paste_shifted: bool = False) -> object:
        if self.pjs._copied_poly_ is None or self.pjs._copied_poly_ == []:
            return False

        if paste_shifted:
            copied_poly = (RUtils.qpolygonf2ndarray(self.pjs._copied_poly_) + RCBCopyPastePolyline.PIX_SHIFT).tolist()
        else:
            copied_poly = RUtils.qpolygonf2list(self.pjs._copied_poly_)

        self.pjs.addPolyline(copied_poly, self.pjs.curslice)

        return True

