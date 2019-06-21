# /********************************************************************************
# * Copyright © 2018-2019, ETH Zurich, D-BSSE, Andreas P. Cuny & Gotthold Fläschner
# * All rights reserved. This program and the accompanying materials
# * are made available under the terms of the GNU Public License v3.0
# * which accompanies this distribution, and is available at
# * http://www.gnu.org/licenses/gpl
# *
# * Contributors:
# *     Andreas P. Cuny - initial API and implementation
# *******************************************************************************/

import os
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QGridLayout, QLabel, QFileDialog, QLineEdit, QDialog, QDialogButtonBox
from pyIMD.ui.resource_path import resource_path


__author__ = 'Andreas P. Cuny'


class ConcatenateFiles(QDialog):
    """
    Implementation of the file concatenation dialog
    """

    def __init__(self, parent=None):
        super(ConcatenateFiles, self).__init__(parent)
        self.setWindowTitle('pyIMD :: Concatenate data files')
        self.resize(150, 150)
        self.setWindowIcon(QtGui.QIcon(resource_path(os.path.join(os.path.join("ui", "icons",
                                                                               "pyIMD_logo_icon.ico")))))
        self.directory = []
        grid = QGridLayout()
        grid.setContentsMargins(5, 5, 5, 5)

        self.intro_label = QLabel('Concatenate measurement data saved in multiple files into a single one.')
        self.time_label = QLabel('Enter the acquisition time interval (in seconds):')
        self.time_interval_edit = QLineEdit(self)
        self.time_interval_edit.textChanged.connect(self.on_time_interval_changed)
        validator = QtGui.QDoubleValidator()
        self.time_interval_edit.setValidator(validator)

        self.directory_label = QLabel('Select directory containing all files to be concatenated:')
        self.directory_edit = QLineEdit(self)
        self.directory_edit.setStyleSheet("background-color: transparent; ")
        self.directory_edit.setReadOnly(1)
        self.directory_edit.textChanged.connect(self.on_directory_changed)
        self.select_dir_btn = QPushButton('Directory')
        self.select_dir_btn.clicked.connect(self.on_dir_selection)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.on_accept)
        buttons.rejected.connect(self.reject)

        grid.addWidget(self.intro_label, 0, 0, 1, 2)
        grid.addWidget(self.directory_label, 1, 0)
        grid.addWidget(self.select_dir_btn, 1, 1)
        grid.addWidget(self.directory_edit, 2, 0, 1, 2)
        grid.addWidget(self.time_label, 3, 0)
        grid.addWidget(self.time_interval_edit, 3, 1)

        grid.addWidget(buttons, 5, 1)
        self.setLayout(grid)

    @staticmethod
    def get_user_input(parent=None):
        dialog = ConcatenateFiles(parent)
        result = dialog.exec_()
        directory = dialog.directory
        time_interval = float(dialog.time_interval_edit.text())
        return (directory, time_interval, result == QDialog.Accepted)

    def on_accept(self):
        if not self.time_interval_edit.text() or not self.directory:
            if not self.time_interval_edit.text():
                self.time_interval_edit.setStyleSheet("background-color: #f6989d;")
            if not self.directory:
                self.directory_edit.setStyleSheet("background-color: #f6989d;")
        else:
            self.accept()

    def on_dir_selection(self):
        self.directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.directory_edit.setText(self.directory)

    def on_time_interval_changed(self):
        self.time_interval_edit.setStyleSheet("background-color: #c4df9b;")

    def on_directory_changed(self):
        self.directory_edit.setStyleSheet("background-color: #c4df9b;")

    def on_close(self):
        self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
