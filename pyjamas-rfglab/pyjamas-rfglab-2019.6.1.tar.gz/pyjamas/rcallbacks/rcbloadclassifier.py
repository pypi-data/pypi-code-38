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

import gzip
import os
import pickle

from PyQt5 import QtWidgets
from sklearn.linear_model.logistic import LogisticRegression
from sklearn.svm.classes import SVC

from pyjamas.rcallbacks.rcallback import RCallback
from pyjamas.rimage.rimclassifier.rimclassifier import rimclassifier
from pyjamas.rimage.rimclassifier.rimlr import lr
from pyjamas.rimage.rimclassifier.rimsvm import svm



class RCBLoadClassifier(RCallback):
    def cbLoadClassifier(self, filename: str = '') -> bool:  # Handle IO errors
        # Get file name.
        if filename == '' or filename is False: # When the menu option is clicked on, for some reason that I do not understand, the function is called with filename = False, which causes a bunch of problems.
            fname = QtWidgets.QFileDialog.getOpenFileName(None, 'Load classifier ...', self.pjs.cwd,
                                                          filter='PyJAMAS classifier (*' + rimclassifier.CLASSIFIER_EXTENSION + ')')  # fname[0] is the full filename, fname[1] is the filter used.
            filename = fname[0]
            if filename == '':
                return False

        # Open file name and read classifier.
        fh = None
        theparameters: dict = None

        try:
            fh = gzip.open(filename, "rb")
            theparameters = pickle.load(fh)

        except (IOError, OSError) as ex:
            if fh is not None:
                fh.close()

            print(ex)
            return False


        if type(theparameters['classifier']) is SVC:
            self.pjs.batch_classifier.image_classifier = svm(theparameters)
        elif type(theparameters['classifier']) is LogisticRegression:
            self.pjs.batch_classifier.image_classifier = lr(theparameters)
        else:
            self.pjs.statusbar.showMessage(f"Wrong classifier type.")
            return False

        # Modify current path.
        self.pjs.cwd = filename[0:filename.rfind(os.sep)]

        self.pjs.statusbar.showMessage(f"Classifier {filename} loaded.")

        return True

