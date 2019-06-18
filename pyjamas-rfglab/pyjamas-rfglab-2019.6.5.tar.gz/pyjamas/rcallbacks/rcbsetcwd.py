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

import os

from PyQt5 import QtWidgets

from .rcallback import RCallback


class RCBSetCWD(RCallback):
    def cbSetCWD(self, folder_name: str = '') -> bool:
        if folder_name == '' or folder_name is False: # When the menu option is clicked on, for some reason that I do not understand, the function is called with filename = False, which causes a bunch of problems.
            folder_name = QtWidgets.QFileDialog.getExistingDirectory(None, 'Save files to folder ...', self.pjs.cwd)  # fname[0] is the full filename, fname[1] is the filter used.

            # If cancel ...
            if folder_name == '':
                return False

        if os.path.exists(folder_name):
            self.pjs.cwd = os.path.abspath(folder_name)
            self.pjs.statusbar.showMessage(f"Working folder set to {self.pjs.cwd}.")

            return True

        else:
            return False