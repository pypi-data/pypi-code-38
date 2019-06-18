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
from pyjamas.rimage.rimclassifier.rimclassifier import rimclassifier


class RCBSaveClassifier(RCallback):
    def cbSaveClassifier(self, filename: str = None, theclassifier: rimclassifier = None) -> bool:  # Handle IO errors.
        if theclassifier is None or theclassifier is False:
            if self.pjs.batch_classifier.image_classifier is None:
                return False
            else:
                theclassifier = self.pjs.batch_classifier.image_classifier

        # Get file name.
        if filename is None or filename is False: # When the menu option is clicked on, for some reason that I do not understand, the function is called with filename = False, which causes a bunch of problems.
            defaultname, _ = os.path.splitext(os.path.basename(self.pjs.filename))
            fname = QtWidgets.QFileDialog.getSaveFileName(None, 'Save classifier ...', self.pjs.cwd + os.sep + defaultname,
                                                          filter='PyJAMAS classifier (*' + rimclassifier.CLASSIFIER_EXTENSION + ')')  # fname[0] is the full filename, fname[1] is the filter used.

            # If cancel ...
            if fname == '':
                return False

            # else ...
            else:
                filename = fname[0]

        if filename[-4:] != rimclassifier.CLASSIFIER_EXTENSION:
            filename = filename + rimclassifier.CLASSIFIER_EXTENSION

        self.pjs.cwd = os.path.dirname(filename)

        theclassifier.save_classifier(filename)

        self.pjs.statusbar.showMessage(f'Saved {filename}.')

        return True

